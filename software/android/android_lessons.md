# Living Memory: Android Companion App Lessons

This document records technical invariants, Gradle/AGP compatibility rules, Jetpack Compose UI behaviors, Room SQLite architecture, and device communication lessons discovered during development of the Smart Crossword Board companion app.

---

## 1. Gradle, Java & Toolchain Invariants

* **LESSON-AND-001 (Java 25 & Gradle 9.1 Compatibility)**:
  * *Symptom/Error*: Android Gradle Plugin (AGP) builds may log `restricted method in java.lang.System has been called` when using cutting-edge Java 25 (`/opt/android-studio/jbr`).
  * *Root Cause*: Java 25 enforces strict encapsulation and native access warnings for certain build tools.
  * *Reliable Mitigation*: Gradle 9.1+ has native Java 25 support. Ensure `JAVA_HOME=/opt/android-studio/jbr` is exported, and ensure Gradle wrapper uses 9.1+ (`gradle-9.1.0-bin.zip`).

* **LESSON-AND-002 (SDK XML Schema Version Invariant)**:
  * *Symptom/Error*: `Warning: SDK processing. This version only understands SDK XML versions up to 3 but an SDK XML file of version 4 was encountered.`
  * *Root Cause*: Minor version skew between Android Studio preview components and AGP template defaults.
  * *Reliable Mitigation*: Non-fatal build warning. Builds succeed normally with `compileSdk = 36` or `37` and `targetSdk = 36`.

---

## 2. Jetpack Compose & UI Invariants

* **LESSON-AND-003 (Interactive Grid State Hoisting)**:
  * *Problem*: In a 4x4 or 15x15 interactive board, triggering a recomposition of the entire board when a single cell changes causes touch jank and lost gesture focus.
  * *Reliable Mitigation*: Hoist cell state into immutable `SnapshotStateList<BoardSquare>` or immutable data classes with `@Stable` annotations. Use `key(row, col)` in LazyVerticalGrid or Column/Row loops so only the modified square redraws.

* **LESSON-AND-004 (Touch Target Sizing for Senior Ergonomics)**:
  * *Ergonomic Invariant*: Every board tile and rack slot must meet Android accessibility guidelines: minimum touch target of **48dp x 48dp** (or use content padding around smaller cells). On vertical phone screens, a 4x4 board easily achieves 72dp x 72dp per square with tactile wooden elevation.

---

## 3. Local-First Room & Cloud Sync Invariants

* **LESSON-AND-005 (Local-First Offline State Contract)**:
  * *Requirement*: Senior players and phone players must never experience blank screens or blocking spinners if internet drops.
  * *Architecture Invariant*: Room SQLite is the Single Source of Truth (SSOT). The UI observes Flow / StateFlow from Room DAOs. Cloud Firestore updates Room in the background; UI never reads directly from network endpoints.

---

## 4. Android Studio & Template Scaffolding Invariants

* **LESSON-AND-006 (Template Scaffolding Directory Invariant)**:
  * *Symptom/Error*: `ERROR: Cannot create template: Directory '...' is not empty`.
  * *Root Cause*: The Google `android create` command strictly requires the target output directory to either be non-existent or completely empty.
  * *Reliable Mitigation*: Keep output directory clean when running `android create`. Store external documentation or README files outside until initial scaffolding completes.

* **LESSON-AND-007 (Material 3 TopAppBar & Icon Scoping)**:
  * *Symptom/Error*: `Unresolved reference 'icons'` or `This material API is experimental`.
  * *Root Cause*: Extended Material Icons (`androidx.compose.material:material-icons-extended`) are not included in baseline Material 3. `CenterAlignedTopAppBar` requires `@OptIn(ExperimentalMaterial3Api::class)` and uses `TopAppBarDefaults.topAppBarColors`.
  * *Reliable Mitigation*: Apply `@OptIn(ExperimentalMaterial3Api::class)` at the Composable/Activity level and use Unicode emoji or local vector drawables for lightweight icons without bloating APK size by 20+ MB.

* **LESSON-AND-008 (Firebase Google Services Gradle Placement & SHA-1 Invariant)**:
  * *Symptom/Error*: Gradle sync fails with `Unresolved reference: id` or syntax errors when pasting Google Services instructions.
  * *Root Cause*: Firebase snippet lines (`id("com.google.gms.google-services")` or dependencies) accidentally pasted inside nested blocks such as `compileOptions { ... }`.
  * *Reliable Mitigation*: In Kotlin DSL (`build.gradle.kts`), plugins must strictly go inside the top-level `plugins { ... }` block, and libraries inside top-level `dependencies { ... }`. Additionally, for Google Sign-In to return tokens, the debug keystore SHA-1 must be registered in the Firebase console before downloading `google-services.json`, otherwise `oauth_client` array remains empty.

* **LESSON-AND-009 (Unmocked Android SDK Stubs in JVM Unit Tests)**:
  * *Symptom/Error*: `java.lang.RuntimeException: Method getJSONObject in org.json.JSONObject not mocked.`
  * *Root Cause*: Pure JVM unit tests (`testDebugUnitTest`) run against Android framework stubs that throw exceptions when invoked unless mocked or configured.
  * *Reliable Mitigation*: Use standard Kotlin/Java string/regex parsing or Kotlinx serialization for JVM tests, or move framework-dependent tests to `androidTest/` (`connectedDebugAndroidTest`) to run on actual Android runtimes.

* **LESSON-AND-010 (OEM Unprivileged ADB DB Cleaning)**:
  * *Symptom/Error*: `java.lang.SecurityException: PID does not have permission android.permission.CLEAR_APP_USER_DATA`.
  * *Root Cause*: OEM distributions (e.g. OnePlus OxygenOS) restrict `adb shell pm clear` for third-party packages on unrooted devices.
  * *Reliable Mitigation*: Use `adb shell "run-as <package> rm -f databases/<dbname>*"` to clear local database files reliably without root permissions.

* **LESSON-AND-011 (Android BLE Descriptor Write Sequencing & ESP32 Partition Size)**:
  * *Symptom/Error*: 1) Second BLE notification subscription (e.g. `SCAN_TELEMETRY`) never triggers callbacks; 2) ESP32 PlatformIO upload fails with flash overflow.
  * *Root Cause*: 1) In Android GATT client, calling `writeDescriptor()` before the previous descriptor write completes drops subsequent subscriptions silently; 2) Standard ESP32 default partition table allocates only 1.25MB for app code, while BLE + SPI consumes ~960KB+, leaving negligible headroom for OTA.
  * *Reliable Mitigation*: 1) Queue all `BluetoothGattDescriptor` write operations in a FIFO list and trigger each next write strictly inside `onDescriptorWrite`; 2) Configure `board_build.partitions = huge_app.csv` in `platformio.ini` to allocate 3MB for app code.

* **LESSON-AND-012 (GATT Connection Hoisting Across Compose Nav Tabs)**:
  * *Symptom/Error*: BLE connection drops immediately whenever the user taps "Friends" or "Account" and navigates away from the game screen.
  * *Root Cause*: Instantiating `BleManager` inside a screen Composable with `remember` and calling `bleManager.disconnect()` inside a `DisposableEffect { onDispose { ... } }` tears down the GATT link whenever the Composable leaves composition during navigation.
  * *Reliable Mitigation*: Hoist `BleManager` to a singleton (`getInstance(context)`) owned by `MainActivity` or the Application lifecycle. Screen Composables observe StateFlows (`connectionState`, `scanTelemetry`, `boardState`) without owning the connection lifecycle. Implement an auto-reconnect loop in `BleManager` that retries every 3 seconds if disconnected unexpectedly.

* **LESSON-AND-013 (Hardware Registration State Guarding & In-App Disabling)**:
  * *Symptom/Error*: User accidentally registers a blank square or links a letter to a previous tag's cached UID if the registration button remains clickable while no tag is present.
  * *Root Cause*: Relying only on `connectionState` to enable hardware mutation actions without binding the button's `enabled` state to live RF telemetry (`telemetry.status == STATUS_TAG_DETECTED && !telemetry.tagUid.isNullOrBlank()`).
  * *Reliable Mitigation*: Gate physical hardware write actions with composite preconditions (`val canEnroll = isConnected && hasTagDetected`). Provide contextual button labeling ("No Tag Detected on Square X" vs "Register Tag ...") and explicit disabled styling (`disabledContainerColor = Color(0xFFCFD8DC)`).

* **LESSON-AND-014 (Latching Telemetry Across Heartbeat Notifications)**:
  * *Symptom/Error*: Tag detection UI flickers or the registration button repeatedly enables and disables itself every 400ms when a tag is sitting on the board.
  * *Root Cause*: The embedded board streams periodic lightweight telemetry pulses (e.g. `[channel, STATUS_ENERGIZED]`) without payload bytes to drive the UI radar animation. When the client deserializes this into `ScanTelemetry`, it assigns `tagUid = null`, inadvertently destroying persistent tag identity on every heartbeat frame.
  * *Reliable Mitigation*: In `BleManager`, latch previously detected `tagUid` for the active channel when an incoming packet is a probing pulse (`STATUS_ENERGIZED`). Only clear the latch when `STATUS_IDLE (0)` (explicit removal) is received or when the user switches to a different channel.

* **LESSON-AND-015 (Persistent Local Tag Identity & ESP32 Reflash Auto-Healing)**:
  * *Symptom/Error*: Physical NFC tile registrations are lost whenever the ESP32 MCU is reflashed or factory-reset during development, reverting registered letters to `'?'`.
  * *Root Cause*: Relying solely on microcontroller NVS storage for physical hardware inventory without a companion phone-side persistent anchor.
  * *Reliable Mitigation*: Store physical tile records (`TileRecord(uid, letter, points, registeredAt)`) in the phone's local SQLite database (`crossword_companion.db`). On BLE service discovery and whenever incoming telemetry reports a tag with `'?'` status, query local SQLite by UID and dispatch `CMD_SYNC_TILE (0x06)` to seamlessly auto-heal and sync the tile mapping to the hardware with zero user friction.

* **LESSON-AND-016 (SQLiteOpenHelper Connection Pool Lifecycle & Concurrency Invariant)**:
  * *Symptom/Error*: Intermittent fatal crashes: `java.lang.IllegalStateException: Cannot perform this operation because the connection pool has been closed` or `attempt to re-open an already-closed object: SQLiteDatabase`.
  * *Root Cause*: Wrapping helper methods in Kotlin's `writableDatabase.use { db -> ... }` or `readableDatabase.use { db -> ... }`. In Android's `SQLiteOpenHelper`, calling `close()` on the database closes the single shared connection pool for the entire application. When background coroutines (e.g. `BleManager` in `Dispatchers.IO`) perform concurrent tile lookups during BLE packet processing while another thread finishes a query, the closed pool throws an uncatchable runtime exception.
  * *Reliable Mitigation*: Only close the `Cursor` (via `cursor.use { ... }`). Never call `.use` or `.close()` on `readableDatabase` or `writableDatabase` within individual DAO methods; leave the database connection lifecycle management to `SQLiteOpenHelper` and Android's Application context.






