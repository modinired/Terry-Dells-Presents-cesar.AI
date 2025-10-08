import UIKit
import Network
import AVFoundation

class ViewController: UIViewController {

    var browser: NWBrowser?
    var connection: NWConnection?
    var audioPlayer: AVAudioPlayer?

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .white
        setupUI()
        startBrowsing()
    }

    func setupUI() {
        let label = UILabel()
        label.text = "Searching for User_Dash Agent..."
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)

        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    func startBrowsing() {
        // Create a browser to find the Bonjour service advertised by the macOS app
        let parameters = NWParameters.tcp
        browser = NWBrowser(for: .bonjour(type: "_userdash._tcp", domain: nil), using: parameters)

        browser?.stateUpdateHandler = { newState in
            switch newState {
            case .ready:
                print("Client browser ready.")
            case .failed(let error):
                print("Client browser failed with error: \(error)")
                self.browser?.cancel()
            default:
                break
            }
        }

        browser?.browseResultsChangedHandler = { (results, changes) in
            for result in results {
                if case .service = result.endpoint {
                    print("Found service: \(result.endpoint)")
                    // For simplicity, connect to the first service found
                    if self.connection == nil {
                        self.connect(to: result.endpoint)
                    }
                }
            }
        }

        browser?.start(queue: .main)
    }

    func connect(to endpoint: NWEndpoint) {
        print("Connecting to \(endpoint)...")
        self.connection = NWConnection(to: endpoint, using: .tcp)

        self.connection?.stateUpdateHandler = { [weak self] (newState) in
            switch newState {
            case .ready:
                print("Connection ready.")
                self?.receive()
            case .failed(let error):
                print("Connection failed with error: \(error)")
                self?.connection?.cancel()
                self?.connection = nil
            default:
                break
            }
        }

        self.connection?.start(queue: .main)
    }

    func receive() {
        connection?.receive(minimumIncompleteLength: 1, maximumLength: 65536) { (content, contentContext, isComplete, error) in
            if let content = content, let message = String(data: content, encoding: .utf8) {
                print("Received message: \(message)")
                if message == "RING" {
                    self.playSound()
                }
            }
            if error == nil {
                self.receive() // Wait for the next message
            }
        }
    }

    func playSound() {
        // Play a standard system sound. This is more reliable than bundling a custom audio file.
        // 1304 is a common SMS/alert sound.
        AudioServicesPlayAlertSound(SystemSoundID(1304))
        print("Playing system sound.")
    }
}