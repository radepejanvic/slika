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
}


export function deactivate() {
    if (!client) return undefined;
    return client.stop();
}