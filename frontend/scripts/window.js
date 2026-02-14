console.log("window.js loaded");

function readTextField() {
    // Find the discord message input field
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            func: function() {


                // Select all chat message containers
                const messageContainers = document.querySelectorAll('li.messageListItem__5126c');
                const messages = {'current-input': 'null', 'chat-history': []};

                // typing input field
                var inputField = document.querySelector('span[data-slate-string="true"]');
                console.log("inputField: " + inputField);
                var typedMessage = inputField ? inputField.innerText : null;

                messages['current-input'] = typedMessage;

                
                var last_username = "";
                messageContainers.forEach(container => {
                    // Extract username
                    const usernameElement = container.querySelector('.username_c19a55');
                    var username = usernameElement ? usernameElement.textContent : 'Unknown';
                    if (username != 'Unknown') {
                        last_username = username;
                    } else {
                        username = last_username;
                    }

                    // Extract timestamp
                    const timestampElement = container.querySelector('.timestamp_c19a55 time');
                    const timestamp = timestampElement ? timestampElement.getAttribute('datetime') : null;

                    // Extract message content
                    const messageContentElement = container.querySelector('.markup__75297.messageContent_c19a55');
                    const messageContent = messageContentElement ? messageContentElement.textContent : null;

                    const imageContainer = container.querySelector('.loadingOverlay_af017a');
                    const imageElement = imageContainer ? imageContainer.querySelector('img') : null;
                    const imageSrc = imageElement ? imageElement.src : null;
                    // Create message object
                    const messageObject = {
                        username: username,
                        timestamp: timestamp,
                        message: messageContent,
                        imageSrc: imageSrc
                    };
                    messages['chat-history'].push(messageObject);

                });
                // Log the messages JSON object
                 console.log(JSON.stringify(messages, null, 2));
                 
                 relatinoship = chrome.runtime.onMessage.addListener(function(request, sender) {
                        console.log("request received: " + JSON.stringify(request));
                        console.log("action received: " + request.action);
                        if (request.action == "sendRelationship") {
                            const typedMessageDiv = document.getElementById("typedMessage");
                            if (request.message) {
                                console.log("User is typing request: " + request.relationship);
                                return request.relationship;
                            } else {
                                console.log("No message found.");
                                return null;
                            }
                        } 
                    }) ? relatinoship : null;

                 try {
                    const response = fetch("http://127.0.0.1:5000/rizzify", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(messages)
                    });
                
                    const data = response.json();
                      if (data.status === "success") {
                        console.log(data.message);  // Show success message
                        //logic from backend
                      } else {
                          // modify the error message
                      }
                    } catch (error) {
                      console.error("Error:", error);
                    }
                
            }  
        });
    });
}
