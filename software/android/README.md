# Smart Crossword Board - Android Companion App

Native Android companion application for the Smart Crossword Board project, allowing players to play Scrabble on their phone against a physical board player or phone-to-phone.

---

## 1. Architecture & Tech Stack

* **Platform**: Native Android (Kotlin, Jetpack Compose, Material 3)
* **Build System**: Gradle 9.1.0 with Android Gradle Plugin 8.13.0 & OpenJDK 25 (`/opt/android-studio/jbr`)
* **Target SDK**: `compileSdk = 36`, `targetSdk = 36`, `minSdk = 26`
* **Game Engine**: Local `EnglishReferee` loaded with full 168,551-word tournament dictionary (`ENABLE1` in `assets/dict_en.txt`)
* **Local Persistence**: SQLite database (`crossword_companion.db`) via `AppDatabaseHelper`
* **Authentication**: Firebase Authentication (`34.18.0`) + Google Play Services Sign-In (`play-services-auth:21.3.0`)
* **Identity Model**: Unique username handles (`name#1234` for players, `board_scb8492` for physical smart boards)

---

## 2. Google Authentication & Firebase Setup

The app is connected to Firebase project **`smart-crossword-2177f`**.

* **Package Name**: `com.example.crosswordcompanion`
* **Debug SHA-1 Certificate Fingerprint**: `93:5F:39:F9:6F:9A:7F:6C:B9:2C:72:AA:E0:6B:1C:7B:56:D1:47:53`
* **Web OAuth Client ID**: `810714924778-6jktq4hnuh4bi4q0inbt13ccfvuvb521.apps.googleusercontent.com`
* **Configuration File**: `software/android/app/google-services.json`
* **Auth Options**:
  * **1-Tap Quick Start**: Instant local guest player with auto-generated unique handle.
  * **Google Account**: Authenticates via Google Play Services and Firebase Auth, retrieving display name, email, and permanent Firebase UID.

---

## 3. Database Management & Live Inspection

The app persists user sessions, paired friends, and game history locally in SQLite.

### Database Inspector Script (`inspect_db.sh`)
From the repository root, run:
```bash
# View live tables and rows from connected device
./software/android/inspect_db.sh

# Reset and wipe database on connected device
./software/android/inspect_db.sh --clear
```

### In-App Reset
Players can also tap **`🗑️ Reset & Clear Local Database`** in the **Account** tab to clear local records and reset to default initial state.

---

## 4. Verification & Automated Test Suites

### A. JVM Unit Tests (15 Tests)
Run all JVM unit tests:
```bash
cd software/android
./gradlew testDebugUnitTest
```
Tests cover:
* `FirebaseConfigTest`: Validates `google-services.json` project ID, package name, debug SHA-1, and Web Client ID.
* `RefereeTest`: Center star rule, 2W/3W/2L/3L multipliers, letter scores for all 26 letters, vertical/horizontal word placement, invalid word rejection, gap rejection, and 168k tournament dictionary verification.
* `MainScreenViewModelTest`: View model initialization and state updates.

### B. On-Device Hardware Tests (6 Tests)
Run instrumented tests on connected physical device or emulator:
```bash
cd software/android
./gradlew connectedDebugAndroidTest
```
Tests cover:
* `AppDatabaseDeviceTest`: Validates SQLite database creation, initial board friend seeding (`board_scb8492`), user save, session exclusivity, user logout, friend creation/retrieval, and full database clearing.
* `MainScreenTest`: Compose UI hierarchy tests.

---

## 5. Living Memory & Invariants

Technical lessons, Gradle placement rules, and OEM Android quirks are maintained in:
`software/android/android_lessons.md`
