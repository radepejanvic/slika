import path from 'path';
import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';

let client: LanguageClient;
let backendStatusBar: vscode.StatusBarItem;
let currentBackend: string = 'cpu';

function binPath(context: vscode.ExtensionContext, name: string): string {
    const exe = process.platform === 'win32' ? `${name}.exe` : name;
    return path.join(context.extensionPath, 'bin', exe);
}

export function activate(context: vscode.ExtensionContext) {
    const serverOptions: ServerOptions = {
        command: binPath(context, 'slika-ls'),
        args: [],
        transport: TransportKind.stdio
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{scheme: 'file', language:'slika'}],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.sl')
        }, 
    }

    client = new LanguageClient(
        'slika',
        'Slika Language Server',
        serverOptions,
        clientOptions
    )

    client.start();

    const runCommand = vscode.commands.registerCommand('slika.run', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active .sl file to run.');
            return;
        }

        const filePath = editor.document.fileName;
        const cliPath = binPath(context, 'slika-cli');

        editor.document.save().then(() => {
            const terminal = vscode.window.createTerminal('Slika');
            terminal.show();
            terminal.sendText(`& "${cliPath}" "${filePath}" --backend ${currentBackend}`);
        });
    });

    context.subscriptions.push(runCommand);

    backendStatusBar = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right, 100
    );
    backendStatusBar.command = 'slika.selectBackend';
    backendStatusBar.tooltip = 'Select Slika processing backend';
    updateStatusBar();
    backendStatusBar.show();
    context.subscriptions.push(backendStatusBar);

    const selectBackendCommand = vscode.commands.registerCommand('slika.selectBackend', async () => {
        const pick = await vscode.window.showQuickPick(
            [
                { label: '$(cpu) CPU',  description: 'OpenCV (default)', value: 'cpu'  },
                { label: '$(rocket) GPU',  description: 'OpenCL accelerated', value: 'gpu'  },
                { label: '$(sync) Auto', description: 'Detect automatically', value: 'auto' },
            ],
            { placeHolder: 'Select processing backend' }
        );
        if (pick) {
            currentBackend = pick.value;
            updateStatusBar();
        }
    });

    context.subscriptions.push(selectBackendCommand);

    const previewCommand = vscode.commands.registerCommand('slika.preview', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const text = editor.document.getText();

        const saveMatch = text.match(/save\s+\w+\s+to\s+"([^"]+)"/);

        if (!saveMatch) {
            vscode.window.showWarningMessage('No save statement found in this file.');
            return;
        }

        const dir = path.dirname(editor.document.fileName);
        const outputPath = path.isAbsolute(saveMatch[1])
            ? saveMatch[1]
            : path.resolve(dir, saveMatch[1]);

        vscode.window.showInformationMessage(
            `Trying to open: ${outputPath}`
        );

        const outputUri = vscode.Uri.file(outputPath);

        vscode.commands.executeCommand('vscode.open', outputUri);
    });

    context.subscriptions.push(previewCommand);
}

function updateStatusBar() {
    const icons: Record<string, string> = {
        'cpu': '$(cpu)',
        'gpu': '$(rocket)',
        'auto': '$(sync)',
    };
    backendStatusBar.text = `${icons[currentBackend] || ''} Slika: ${currentBackend.toUpperCase()}`;
}


export function deactivate() {
    if (!client) return undefined;
    return client.stop();
}