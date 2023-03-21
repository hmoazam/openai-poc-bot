# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import requests

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    CardFactory,
    MessageFactory,
)
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)

from data_models import WelcomeUserState


class WelcomeUserBot(ActivityHandler):
    def __init__(self, user_state: UserState):
        if user_state is None:
            raise TypeError(
                "[WelcomeUserBot]: Missing parameter. user_state is required but None was given"
            )

        self._user_state = user_state

        self.user_state_accessor = self._user_state.create_property("WelcomeUserState")

        self.WELCOME_MESSAGE = """Welcome to the Kahramaa Open AI Assistant. Ask a question to get started."""

        # self.INFO_MESSAGE = """You are seeing this message because the bot received at least one
        #                 'ConversationUpdate' event, indicating you (and possibly others)
        #                 joined the conversation. If you are using the emulator, pressing
        #                 the 'Start Over' button to trigger this event again. The specifics
        #                 of the 'ConversationUpdate' event depends on the channel. You can
        #                 read more information at: https://aka.ms/about-botframework-welcome-user"""

        # self.LOCALE_MESSAGE = """"You can use the 'activity.locale' property to welcome the
        #                 user using the locale received from the channel. If you are using the 
        #                 Emulator, you can set this value in Settings."""

        # self.PATTERN_MESSAGE = """It is a good pattern to use this event to send general greeting
        #                 to user, explaining what your bot can do. In this example, the bot
        #                 handles 'hello', 'hi', 'help' and 'intro'. Try it now, type 'hi'"""

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # save changes to WelcomeUserState after each turn
        await self._user_state.save_changes(turn_context)

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        """
        Greet when users are added to the conversation.
        Note that all channels do not send the conversation update activity.
        If you find that this bot works in the emulator, but does not in
        another channel the reason is most likely that the channel does not
        send this activity.
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    self.WELCOME_MESSAGE
                )

                # await turn_context.send_activity(self.INFO_MESSAGE)

                # await turn_context.send_activity(
                #     f"{ self.LOCALE_MESSAGE } Current locale is { turn_context.activity.locale }."
                # )

                # await turn_context.send_activity(self.PATTERN_MESSAGE)

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Respond to messages sent from the user.
        """
        # Get the state properties from the turn context.
        welcome_user_state = await self.user_state_accessor.get(
            turn_context, WelcomeUserState
        )

        # if not welcome_user_state.did_welcome_user:
        #     welcome_user_state.did_welcome_user = True

        #     # await turn_context.send_activity(
        #     #     "You are seeing this message because this was your first message ever to this bot."
        #     # )

        #     # name = turn_context.activity.from_property.name
        #     # await turn_context.send_activity(
        #     #     f"It is a good practice to welcome the user and provide personal greeting. For example: Welcome {name}"
        #     # )

        # else:
        # This example hardcodes specific utterances. You should use LUIS or QnA for more advance language
        # understanding.
        text = turn_context.activity.text.lower()

        if text in ("intro", "help"):
            await self.__send_intro_card(turn_context)
        # if text == "view context":
        #     await self.

        response = requests.post("https://funcappkmopai.azurewebsites.net/api/BotQnAHTTPFunc?code=nsdg33_Yail7DCmpqxH28ZycD-R_c5YH6PYppxMBTLP2AzFuAN6zQg==", json={"query": text})
        if response.status_code == 200:
            if response.json()['answer'] != "Sorry, the query did not find a good match. Please rephrase your question.":
                await self.__send_intro_card(turn_context, response.json()['answer'], response.json()['link'], response.json()['context'])
            else:
                await turn_context.send_activity("Sorry, the query did not find a good match. Please rephrase your question.")
            # await turn_context.send_activity(response.json()['answer'])
        else:
            await turn_context.send_activity("Connection reset, please retry")

        # if text in ("hello", "hi"):
        #     await turn_context.send_activity(f"You said { text }")
        
        # else:
        #     await turn_context.send_activity(self.WELCOME_MESSAGE)



    async def __send_intro_card(self, turn_context: TurnContext, answer, doc_url, context):
        card = HeroCard(
            # title="Welcome to Bot Framework!",
            text= answer,
            # images=[CardImage(url="https://aka.ms/bf-welcome-card-image")],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="View Document",
                    text="View Document",
                    display_text="View Document",
                    value=doc_url,
                )
            ],
        )

        return await turn_context.send_activity(
            MessageFactory.attachment(CardFactory.hero_card(card))
        )
