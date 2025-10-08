import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import { AgentViewProvider } from './AgentViewProvider';

const childProcesses: Map<string, ChildProcess> = new Map();

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "llm-integrator" is now active!');

	const provider = new AgentViewProvider(context.extensionUri);

	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(AgentViewProvider.viewType, provider));

	// Listen for messages from the webview
	provider.getWebviewView()?.webview.onDidReceiveMessage(message => {
		if (message.type === 'response') {
			const process = childProcesses.get(message.agentId);
			if (process) {
				process.stdin?.write(`${message.answer}\n`);
			}
		}
	});

	const agentCommands = vscode.workspace.getConfiguration('llm-integrator').get<string[]>('agents');

	if (agentCommands && agentCommands.length > 0) {
		agentCommands.forEach(command => {
			// Using shell: true is better for handling complex commands
			const child = spawn(command, [], { shell: true });
			const agentId = `agent_${child.pid}`;
			childProcesses.set(agentId, child);

			child.stdout.on('data', (data) => {
				const output = data.toString();
				console.log(`[${agentId}] stdout: ${output}`);
				provider.addMessage({ agentId, text: output });
			});

			child.stderr.on('data', (data) => {
				const output = data.toString();
				console.error(`[${agentId}] stderr: ${output}`);
				provider.addMessage({ agentId, text: `ERROR: ${output}` });
			});

			child.on('close', (code) => {
				console.log(`child process ${agentId} exited with code ${code}`);
				provider.addMessage({ agentId, text: `Agent exited with code ${code}.`});
				childProcesses.delete(agentId);
			});

			child.on('error', (err) => {
				console.error(`Failed to start subprocess for command: ${command}. Error: ${err.message}`);
				provider.addMessage({ agentId, text: `Failed to start agent: ${err.message}`});
				childProcesses.delete(agentId);
			});
		});
	}
}

export function deactivate() {
	childProcesses.forEach((child) => {
		child.kill();
	});
}