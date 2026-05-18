import path from 'path';
import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const lspPath = path.join(context.extensionPath, '..', 'src', 'lsp.py');
    
    const serverOptions: ServerOptions = {
        command: '/home/trajcex/Desktop/slika/.venv/bin/python',
        args: [lspPath],
        options: {
            cwd: path.join(context.extensionPath, '..')
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