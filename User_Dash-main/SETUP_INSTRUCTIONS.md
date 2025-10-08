# Setup Instructions for User_Dash Agent

This document provides the steps to compile and run the macOS voice agent and its companion iOS app. Since I cannot create full Xcode projects, you will need to follow these instructions to create the projects and add the provided source code.

**Prerequisites:**
*   A MacBook running a recent version of macOS.
*   An iPhone running a recent version of iOS.
*   Xcode installed on your MacBook.
*   Both devices must be on the same local Wi-Fi network.

---

## Part 1: Create the macOS Agent (`User_Dash_Agent`)

This application will run in your Mac's status bar, listen for voice commands, and send them to your iPhone.

1.  **Create a New Xcode Project:**
    *   Open Xcode and select **File > New > Project...**.
    *   Choose the **macOS** tab and select the **App** template. Click **Next**.
    *   Product Name: `User_Dash_Agent`
    *   Interface: **Storyboard**
    *   Language: **Swift**
    *   Uncheck "Use Core Data" and "Include Tests". Click **Next**.
    *   Save the project somewhere on your Mac.

2.  **Add the Source Files:**
    *   In the Xcode project navigator (the left-hand pane), right-click on the `User_Dash_Agent` folder and select **Add Files to "User_Dash_Agent"...**.
    *   Navigate to the `macOS/User_Dash_Agent` directory I have created.
    *   Select the `AppDelegate.swift` file and add it to the project. **Important:** When prompted, choose to **Replace** the existing `AppDelegate.swift` file.
    *   Repeat the process for the `Main.storyboard` file (located in the `Base.lproj` folder). Again, choose to **Replace** the existing file.

3.  **Configure the `Info.plist`:**
    *   In the Xcode project navigator, find and select the `Info.plist` file.
    *   Right-click in the empty space below the existing keys and select **Add Row**.
    *   Add the following two keys and their corresponding string values. This is required for privacy permissions.
        *   **Key:** `Privacy - Microphone Usage Description`
        *   **Value:** `This app needs microphone access to listen for your voice commands.`
        *   **Key:** `Privacy - Speech Recognition Usage Description`
        *   **Value:** `This app uses speech recognition to control your phone.`

4.  **Run the Agent:**
    *   Press the **Run** button (the triangle icon) in the top-left of the Xcode window.
    *   The app will launch, and you should see a "🎤" icon appear in your Mac's status bar at the top of the screen.
    *   The first time you run it, you may be prompted to grant microphone and speech recognition permissions. **You must allow these.**

---

## Part 2: Create the iOS Companion App (`User_Dash_Companion`)

This app runs on your iPhone, listens for commands from the Mac agent, and performs the requested action (like playing a sound).

1.  **Create a New Xcode Project:**
    *   Open Xcode and select **File > New > Project...**.
    *   Choose the **iOS** tab and select the **App** template. Click **Next**.
    *   Product Name: `User_Dash_Companion`
    *   Interface: **Storyboard**
    *   Language: **Swift**
    *   Uncheck "Use Core Data" and "Include Tests". Click **Next**.
    *   Save the project.

2.  **Add the Source Files:**
    *   In the Xcode project navigator, right-click on the `User_Dash_Companion` folder and select **Add Files to "User_Dash_Companion"...**.
    *   Navigate to the `iOS/User_Dash_Companion` directory I have created.
    *   Select `AppDelegate.swift` and `ViewController.swift`. Add them to the project, choosing to **Replace** the existing files when prompted.

3.  **Configure the `Info.plist`:**
    *   In the Xcode project navigator, find and select `Info.plist`.
    *   Right-click and **Add Row**.
    *   Add the following key and value to allow the app to search for the Mac agent on your network.
        *   **Key:** `Privacy - Local Network Usage Description`
        *   **Value:** `This app needs to connect to the local network to find the macOS agent.`
    *   Add another key to declare the Bonjour service it will be looking for.
        *   **Key:** `Bonjour services`
        *   This key is an **Array**. Click the arrow to expand it.
        *   Set **Item 0** to be a **String** with the value: `_userdash._tcp`

4.  **Run the App:**
    *   Connect your iPhone to your MacBook with a USB cable.
    *   In Xcode, select your iPhone from the device list at the top of the window.
    *   Press the **Run** button. The app will be installed and launched on your phone.
    *   The first time it runs, you will be prompted to allow it to find and connect to devices on your local network. **You must allow this.**

---

## Part 3: How to Use

1.  Ensure the **macOS agent is running** (the 🎤 icon is in your status bar).
2.  Ensure the **iOS companion app is running** on your iPhone.
3.  Click the 🎤 icon in the status bar and select **Start Listening**.
4.  Speak clearly into your Mac's microphone: **"Make my phone ring."**
5.  Your iPhone should play a system alert sound.

You have now successfully established the basic connection! The next phases of our project will build on this foundation.