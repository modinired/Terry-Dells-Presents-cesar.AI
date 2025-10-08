// This script will be run in the webview
(function() {
    const vscode = acquireVsCodeApi();
    const eventsList = document.getElementById('events');

    // Handle messages sent from the extension to the webview
    window.addEventListener('message', event => {
        const message = event.data; // The json data that the extension sent
        switch (message.type) {
            case 'addEvent':
                const li = document.createElement('li');
                li.dataset.agentId = message.agentId;

                // Simple heuristic to detect a question
                if (message.text.includes('Would you like to')) {
                    const question = document.createElement('div');
                    question.className = 'question';
                    question.textContent = message.text;
                    li.appendChild(question);

                    const buttonGroup = document.createElement('div');
                    buttonGroup.className = 'button-group';

                    const yesButton = document.createElement('button');
                    yesButton.textContent = 'Yes';
                    yesButton.addEventListener('click', () => {
                        vscode.postMessage({ type: 'response', agentId: message.agentId, answer: 'Yes' });
                        disableButtons(buttonGroup);
                    });
                    buttonGroup.appendChild(yesButton);

                    const noButton = document.createElement('button');
                    noButton.textContent = 'No';
                    noButton.addEventListener('click', () => {
                        vscode.postMessage({ type: 'response', agentId: message.agentId, answer: 'No' });
                        disableButtons(buttonGroup);
                    });
                    buttonGroup.appendChild(noButton);

                    li.appendChild(buttonGroup);
                } else {
                    li.textContent = message.text;
                }

                eventsList.appendChild(li);
                break;
        }
    });

    function disableButtons(buttonGroup) {
        Array.from(buttonGroup.children).forEach(button => {
            button.disabled = true;
        });
    }

}());