import path from 'path';
import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const projectRoot = path.join(context.extensionPath, '..');
    const serverOptions: ServerOptions = {
        command: path.join(projectRoot, '.venv', 'bin', 'python'),
        args: ['-m', 'src.lsp'],
        options: {
            cwd: projectRoot
        },
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

        editor.document.save().then(() => {
            const terminal = vscode.window.createTerminal('Slika');
            terminal.show();
            terminal.sendText(`slika "${filePath}"`);
        });
    });

    context.subscriptions.push(runCommand);
}


export function deactivate() {
    if (!client) return undefined;
    return client.stop();
}