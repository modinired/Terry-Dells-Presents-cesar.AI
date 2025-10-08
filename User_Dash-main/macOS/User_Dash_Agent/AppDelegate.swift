import Cocoa
import Network
import Speech

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    var statusItem: NSStatusItem!
    var listener: NWListener?
    var connection: NWConnection?

    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Create the status bar item
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        if let button = statusItem.button {
            button.title = "🎤"
        }

        // Setup the menu
        setupMenu()

        // Start listening for network connections
        startServer()

        // Request speech recognition authorization
        requestSpeechAuth()
    }

    func setupMenu() {
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Start Listening", action: #selector(startRecording), keyEquivalent: "S"))
        menu.addItem(NSMenuItem(title: "Stop Listening", action: #selector(stopRecording), keyEquivalent: "T"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        statusItem.menu = menu
    }

    func startServer() {
        do {
            // Create a listener on a random port, advertising with Bonjour
            let parameters = NWParameters.tcp
            listener = try NWListener(using: parameters)
            listener?.service = NWListener.Service(name: "UserDashAgent", type: "_userdash._tcp")

            listener?.stateUpdateHandler = { (newState) in
                switch newState {
                case .ready:
                    print("Server ready and listening on port \(self.listener?.port?.debugDescription ?? "N/A")")
                case .failed(let error):
                    print("Server failed with error: \(error)")
                    self.listener?.cancel()
                default:
                    break
                }
            }

            listener?.newConnectionHandler = { (newConnection) in
                print("Accepted new connection")
                if self.connection != nil {
                    print("Replacing existing connection.")
                    self.connection?.cancel()
                }
                self.connection = newConnection
                self.connection?.start(queue: .main)
            }

            listener?.start(queue: .main)
        } catch {
            print("Error starting server: \(error)")
        }
    }

    func sendRingCommand() {
        guard let connection = connection else {
            print("No client connected.")
            return
        }

        let message = "RING".data(using: .utf8)!
        connection.send(content: message, completion: .contentProcessed { (error) in
            if let error = error {
                print("Send error: \(error)")
            } else {
                print("Successfully sent RING command.")
            }
        })
    }

    func requestSpeechAuth() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            OperationQueue.main.addOperation {
                switch authStatus {
                case .authorized:
                    print("Speech recognition authorized.")
                default:
                    print("Speech recognition not authorized.")
                }
            }
        }
    }

    @objc func startRecording() {
        if recognitionTask != nil {
            recognitionTask?.cancel()
            recognitionTask = nil
        }

        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("audioSession properties weren't set because of an error.")
        }

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()

        let inputNode = audioEngine.inputNode
        guard let recognitionRequest = recognitionRequest else {
            fatalError("Unable to create an SFSpeechAudioBufferRecognitionRequest object")
        }

        recognitionRequest.shouldReportPartialResults = true

        recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest, resultHandler: { (result, error) in
            var isFinal = false

            if let result = result {
                let bestString = result.bestTranscription.formattedString
                print("Recognized: \(bestString)")
                if bestString.lowercased().contains("make my phone ring") {
                    self.sendRingCommand()
                    self.stopRecording() // Stop after command is recognized
                }
                isFinal = result.isFinal
            }

            if error != nil || isFinal {
                self.audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                self.recognitionRequest = nil
                self.recognitionTask = nil
            }
        })

        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { (buffer, when) in
            self.recognitionRequest?.append(buffer)
        }

        audioEngine.prepare()

        do {
            try audioEngine.start()
            print("Listening...")
        } catch {
            print("audioEngine couldn't start because of an error.")
        }
    }

    @objc func stopRecording() {
        if audioEngine.isRunning {
            audioEngine.stop()
            recognitionRequest?.endAudio()
            print("Stopped listening.")
        }
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        listener?.cancel()
        connection?.cancel()
    }
}