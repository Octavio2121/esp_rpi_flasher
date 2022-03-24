# Create the SlackBot Class
class SlackBot:

    # Create a constant that contains the default text for the message
    BOT_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                " "
            ),
        },
    }

    # The constructor for the class. It takes the channel name as the a
    # parameter and then sets it as an instance variable
    def __init__(self, channel,code_msg):
        self.channel = channel
        self.code_msg = code_msg

    def _bot_msg(self):
        
        results = self.code_msg

        text = f"{results}"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}},

    # Craft and return the entire message payload as a dictionary.
    def get_message_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self.BOT_BLOCK,
                *self._bot_msg(),
            ],
        }
