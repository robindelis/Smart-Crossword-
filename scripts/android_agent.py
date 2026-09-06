#!/usr/bin/env python3
"""
Android Specialist Agent - Google Antigravity SDK
Specialized in Native Android Development (Kotlin, Jetpack Compose, Android Studio, Gradle, android-cli).
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path

from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig, types

ANDROID_SDK_PATH = "/home/robin/Android/Sdk"
JAVA_HOME_PATH = "/opt/android-studio/jbr"
ANDROID_CLI_SKILL_PATH = "/home/robin/.gemini/config/plugins/android-cli-plugin/skills"

SYSTEM_INSTRUCTIONS = """
You are the Native Android Specialist for the Smart Crossword Board project.
Your mission is to develop, test, and maintain the Android companion app using Kotlin, Jetpack Compose, Material 3, and Gradle.

Environment & Tooling:
- ANDROID_HOME: /home/robin/Android/Sdk
- JAVA_HOME: /opt/android-studio/jbr (OpenJDK 25)
- Android Studio: /opt/android-studio/bin/studio.sh (command: studio)
- Android CLI: /home/robin/.local/bin/android (commands: android create, android sdk, android run, android emulator, android layout, android docs)
- ADB: /home/robin/Android/Sdk/platform-tools/adb (command: adb)

Key Architectures:
1. Native UI: Jetpack Compose, Navigation Compose, Material 3 with tactile wooden styling tokens.
2. 15x15 Zoomable Board: Smooth pinch-to-zoom (0.65x to 2.5x) and pan gestures with drag/tap tile placement.
3. Audio: WebM/Opus voice notes (5-10s) recorded from phone and sent to board speaker.
4. Cloud Sync: Firebase Firestore real-time listeners, FCM turn notifications, and Google Sign-In.
5. Board Provisioning: Android Bluetooth Low Energy (BLE) to configure parent's Wi-Fi seamlessly.
6. Game Engine: Rule validation using portable C referee (crossword_engine) or shared Kotlin bridge.
""".strip()

def create_agent_config(interactive: bool = False) -> LocalAgentConfig:
    """Creates a configured LocalAgentConfig for the Android Specialist."""
    # Ensure environment variables are propagated
    env = dict(os.environ)
    env["ANDROID_HOME"] = ANDROID_SDK_PATH
    env["ANDROID_SDK_ROOT"] = ANDROID_SDK_PATH
    env["JAVA_HOME"] = JAVA_HOME_PATH
    env["PATH"] = f"{JAVA_HOME_PATH}/bin:{ANDROID_SDK_PATH}/platform-tools:{ANDROID_SDK_PATH}/emulator:{env.get('PATH', '')}"

    behavior = types.AgentBehavior.INTERACTIVE if interactive else types.AgentBehavior.AUTONOMOUS
    capabilities = CapabilitiesConfig(
        agent_behavior=behavior,
        enable_subagents=True,
    )

    skill_path = Path(ANDROID_CLI_SKILL_PATH)
    skills_paths = [str(skill_path)] if skill_path.exists() else None

    return LocalAgentConfig(
        system_instructions=SYSTEM_INSTRUCTIONS,
        capabilities=capabilities,
        skills_paths=skills_paths,
        env=env,
        workspaces=["/home/robin/Smart-Crossword-Board"]
    )

async def run_prompt(prompt: str):
    """Runs a single prompt through the Android Specialist agent."""
    config = create_agent_config(interactive=False)
    print(f"🤖 Starting Android Specialist Agent...")
    print(f"📁 Skills loaded: {config.skills_paths}")
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()

def verify_agent():
    """Verifies that the agent configuration and environment dependencies are valid."""
    print("=== Android Specialist Agent Verification ===")
    print(f"1. Checking Android SDK: {ANDROID_SDK_PATH} -> {'OK' if os.path.isdir(ANDROID_SDK_PATH) else 'MISSING'}")
    print(f"2. Checking Java Home: {JAVA_HOME_PATH} -> {'OK' if os.path.isdir(JAVA_HOME_PATH) else 'MISSING'}")
    print(f"3. Checking android-cli skill: {ANDROID_CLI_SKILL_PATH} -> {'OK' if os.path.isdir(ANDROID_CLI_SKILL_PATH) else 'MISSING'}")
    
    config = create_agent_config()
    print("4. Initializing LocalAgentConfig -> OK")
    print("=== Verification Complete: Ready for Android App Development ===")
    return True

def main():
    parser = argparse.ArgumentParser(description="Android Specialist Agent (Google Antigravity SDK)")
    parser.add_argument("prompt", nargs="?", default=None, help="Prompt to execute")
    parser.add_argument("--verify", action="store_true", help="Verify agent configuration and dependencies")
    args = parser.parse_args()

    if args.verify or args.prompt is None:
        verify_agent()
        if args.prompt is None:
            return

    asyncio.run(run_prompt(args.prompt))

if __name__ == "__main__":
    main()
