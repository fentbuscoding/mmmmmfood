# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

import mock
import pytest

from hikari import applications
from hikari import monetization
from hikari import snowflakes
from hikari import traits
from hikari.impl import special_endpoints
from hikari.interactions import base_interactions
from hikari.interactions import command_interactions


@pytest.fixture
def mock_app():
    return mock.Mock(traits.CacheAware, rest=mock.AsyncMock())


class TestCommandInteraction:
    @pytest.fixture
    def mock_command_interaction(self, mock_app):
        return command_interactions.CommandInteraction(
            app=mock_app,
            id=snowflakes.Snowflake(2312312),
            type=base_interactions.InteractionType.APPLICATION_COMMAND,
            channel=mock.Mock(id=3123123),
            guild_id=snowflakes.Snowflake(5412231),
            member=object(),
            user=object(),
            token="httptptptptptptptp",
            version=1,
            application_id=snowflakes.Snowflake(43123),
            command_id=snowflakes.Snowflake(3123123),
            command_name="OKOKOK",
            command_type=1,
            options=[],
            resolved=None,
            locale="es-ES",
            guild_locale="en-US",
            app_permissions=543123,
            registered_guild_id=snowflakes.Snowflake(12345678),
            entitlements=[
                monetization.Entitlement(
                    id=snowflakes.Snowflake(123123),
                    sku_id=snowflakes.Snowflake(123123),
                    application_id=snowflakes.Snowflake(123123),
                    guild_id=snowflakes.Snowflake(123123),
                    user_id=snowflakes.Snowflake(123123),
                    type=monetization.EntitlementType.APPLICATION_SUBSCRIPTION,
                    starts_at=None,
                    ends_at=None,
                    is_deleted=False,
                    subscription_id=None,
                )
            ],
            authorizing_integration_owners={
                applications.ApplicationIntegrationType.GUILD_INSTALL: snowflakes.Snowflake(123)
            },
            context=applications.ApplicationContextType.PRIVATE_CHANNEL,
        )

    def test_channel_id_property(self, mock_command_interaction):
        assert mock_command_interaction.channel_id == 3123123

    def test_build_response(self, mock_command_interaction, mock_app):
        mock_app.rest.interaction_message_builder = mock.Mock()
        builder = mock_command_interaction.build_response()

        assert builder is mock_app.rest.interaction_message_builder.return_value
        mock_app.rest.interaction_message_builder.assert_called_once_with(base_interactions.ResponseType.MESSAGE_CREATE)

    def test_build_deferred_response(self, mock_command_interaction, mock_app):
        mock_app.rest.interaction_deferred_builder = mock.Mock()
        builder = mock_command_interaction.build_deferred_response()

        assert builder is mock_app.rest.interaction_deferred_builder.return_value
        mock_app.rest.interaction_deferred_builder.assert_called_once_with(
            base_interactions.ResponseType.DEFERRED_MESSAGE_CREATE
        )


class TestAutocompleteInteraction:
    @pytest.fixture
    def mock_autocomplete_interaction(self, mock_app):
        return command_interactions.AutocompleteInteraction(
            app=mock_app,
            id=snowflakes.Snowflake(2312312),
            type=base_interactions.InteractionType.APPLICATION_COMMAND,
            channel=mock.Mock(3123123),
            guild_id=snowflakes.Snowflake(5412231),
            guild_locale="en-US",
            locale="en-US",
            app_permissions=123321,
            member=object(),
            user=object(),
            token="httptptptptptptptp",
            version=1,
            application_id=snowflakes.Snowflake(43123),
            command_id=snowflakes.Snowflake(3123123),
            command_name="OKOKOK",
            command_type=1,
            options=[],
            registered_guild_id=snowflakes.Snowflake(12345678),
            entitlements=[
                monetization.Entitlement(
                    id=snowflakes.Snowflake(123123),
                    sku_id=snowflakes.Snowflake(123123),
                    application_id=snowflakes.Snowflake(123123),
                    guild_id=snowflakes.Snowflake(123123),
                    user_id=snowflakes.Snowflake(123123),
                    type=monetization.EntitlementType.APPLICATION_SUBSCRIPTION,
                    starts_at=None,
                    ends_at=None,
                    is_deleted=False,
                    subscription_id=None,
                )
            ],
            authorizing_integration_owners={
                applications.ApplicationIntegrationType.GUILD_INSTALL: snowflakes.Snowflake(123)
            },
            context=applications.ApplicationContextType.PRIVATE_CHANNEL,
        )

    @pytest.fixture
    def mock_command_choices(self):
        return [
            special_endpoints.AutocompleteChoiceBuilder(name="a", value="b"),
            special_endpoints.AutocompleteChoiceBuilder(name="foo", value="bar"),
        ]

    def test_build_response(self, mock_autocomplete_interaction, mock_app, mock_command_choices):
        mock_app.rest.interaction_autocomplete_builder = mock.Mock()
        builder = mock_autocomplete_interaction.build_response(mock_command_choices)

        assert builder is mock_app.rest.interaction_autocomplete_builder.return_value
        mock_app.rest.interaction_autocomplete_builder.assert_called_once_with(mock_command_choices)

    @pytest.mark.asyncio
    async def test_create_response(
        self,
        mock_autocomplete_interaction: command_interactions.AutocompleteInteraction,
        mock_app,
        mock_command_choices,
    ):
        await mock_autocomplete_interaction.create_response(mock_command_choices)

        mock_app.rest.create_autocomplete_response.assert_awaited_once_with(
            2312312, "httptptptptptptptp", mock_command_choices
        )
