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
"""Component that provides the ability to generate event models."""

from __future__ import annotations

__all__: typing.Sequence[str] = ("EventFactory",)

import abc
import typing

if typing.TYPE_CHECKING:
    from hikari import channels as channel_models
    from hikari import emojis as emojis_models
    from hikari import guilds as guild_models
    from hikari import invites as invite_models
    from hikari import messages as messages_models
    from hikari import presences as presences_models
    from hikari import snowflakes
    from hikari import stickers as sticker_models
    from hikari import users as user_models
    from hikari import voices as voices_models
    from hikari.api import shard as gateway_shard
    from hikari.events import application_events
    from hikari.events import auto_mod_events
    from hikari.events import channel_events
    from hikari.events import guild_events
    from hikari.events import interaction_events
    from hikari.events import lifetime_events
    from hikari.events import member_events
    from hikari.events import message_events
    from hikari.events import monetization_events
    from hikari.events import poll_events
    from hikari.events import reaction_events
    from hikari.events import role_events
    from hikari.events import scheduled_events
    from hikari.events import shard_events
    from hikari.events import stage_events
    from hikari.events import typing_events
    from hikari.events import user_events
    from hikari.events import voice_events
    from hikari.internal import data_binding


class EventFactory(abc.ABC):
    """Interface for components that deserialize JSON events."""

    __slots__: typing.Sequence[str] = ()

    ######################
    # APPLICATION EVENTS #
    ######################

    @abc.abstractmethod
    def deserialize_application_command_permission_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> application_events.ApplicationCommandPermissionsUpdateEvent:
        """Parse a raw payload from Discord into an application command permissions update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.application_events.ApplicationCommandPermissionsUpdateEvent
            The parsed application command permissions update event.
        """

    ##################
    # CHANNEL EVENTS #
    ##################

    @abc.abstractmethod
    def deserialize_guild_channel_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.GuildChannelCreateEvent:
        """Parse a raw payload from Discord into a channel create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.GuildChannelCreateEvent
            The parsed channel create event object.
        """

    @abc.abstractmethod
    def deserialize_guild_channel_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_channel: channel_models.PermissibleGuildChannel | None = None,
    ) -> channel_events.GuildChannelUpdateEvent:
        """Parse a raw payload from Discord into a channel update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_channel
            The guild channel object or [`None`][].

        Returns
        -------
        hikari.events.channel_events.GuildChannelUpdateEvent
            The parsed  event object.
        """

    @abc.abstractmethod
    def deserialize_guild_channel_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.GuildChannelDeleteEvent:
        """Parse a raw payload from Discord into a channel delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.GuildChannelDeleteEvent
            The parsed channel delete event object.
        """

    @abc.abstractmethod
    def deserialize_channel_pins_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.PinsUpdateEvent:
        """Parse a raw payload from Discord into a channel pins update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.PinsUpdateEvent
            The parsed channel pins update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_thread_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.GuildThreadCreateEvent:
        """Parse a raw payload from Discord into a guild thread create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.GuildThreadCreateEvent
            The parsed guild thread create event object.
        """

    @abc.abstractmethod
    def deserialize_guild_thread_access_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.GuildThreadAccessEvent:
        """Parse a raw payload from Discord into a guild thread access event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.GuildThreadAccessEvent
            The parsed guild thread create event object.
        """

    @abc.abstractmethod
    def deserialize_guild_thread_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_thread: channel_models.GuildThreadChannel | None = None,
    ) -> channel_events.GuildThreadUpdateEvent:
        """Parse a raw payload from Discord into a guild thread update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_thread
            The guild thread channel object or [`None`][].

        Returns
        -------
        hikari.events.channel_events.GuildThreadUpdateEvent
            The parsed guild thread update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_thread_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.GuildThreadDeleteEvent:
        """Parse a raw payload from Discord into a guild thread delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.GuildThreadDeleteEvent
            The parsed guild thread delete event object.
        """

    @abc.abstractmethod
    def deserialize_thread_members_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.ThreadMembersUpdateEvent:
        """Parse a raw payload from Discord into a thread members update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.ThreadMembersUpdateEvent
            The parsed thread members update event object.
        """

    @abc.abstractmethod
    def deserialize_thread_list_sync_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.ThreadListSyncEvent:
        """Parse a raw payload from Discord into a thread list sync event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.ThreadListSyncEvent
            The parsed thread member list sync event object.
        """

    @abc.abstractmethod
    def deserialize_webhook_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.WebhookUpdateEvent:
        """Parse a raw payload from Discord into a webhook update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.WebhookUpdateEvent
            The parsed webhook update event object.
        """

    @abc.abstractmethod
    def deserialize_invite_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> channel_events.InviteCreateEvent:
        """Parse a raw payload from Discord into an invite create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.channel_events.InviteCreateEvent
            The parsed invite create event object.
        """

    @abc.abstractmethod
    def deserialize_invite_delete_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_invite: invite_models.InviteWithMetadata | None = None,
    ) -> channel_events.InviteDeleteEvent:
        """Parse a raw payload from Discord into an invite delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_invite
            The invite object or [`None`][].

        Returns
        -------
        hikari.events.channel_events.InviteDeleteEvent
            The parsed invite delete event object.
        """

    #################
    # TYPING EVENTS #
    ##################

    @abc.abstractmethod
    def deserialize_typing_start_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> typing_events.TypingEvent:
        """Parse a raw payload from Discord into a typing start event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.typing_events.TypingEvent
            The parsed typing start event object.
        """

    ################
    # GUILD EVENTS #
    ################

    @abc.abstractmethod
    def deserialize_guild_available_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.GuildAvailableEvent:
        """Parse a raw payload from Discord into a guild available event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.GuildAvailableEvent
            The parsed guild create event object.
        """

    @abc.abstractmethod
    def deserialize_guild_join_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.GuildJoinEvent:
        """Parse a raw payload from Discord into a guild join event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.GuildJoinEvent
            The parsed guild join event object.
        """

    @abc.abstractmethod
    def deserialize_guild_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_guild: guild_models.GatewayGuild | None = None,
    ) -> guild_events.GuildUpdateEvent:
        """Parse a raw payload from Discord into a guild update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_guild
            The guild object or [`None`][].

        Returns
        -------
        hikari.events.guild_events.GuildUpdateEvent
            The parsed guild update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_leave_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_guild: guild_models.GatewayGuild | None = None,
    ) -> guild_events.GuildLeaveEvent:
        """Parse a raw payload from Discord into a guild leave event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_guild
            The guild object or [`None`][].

        Returns
        -------
        hikari.events.guild_events.GuildLeaveEvent
            The parsed guild leave event object.
        """

    @abc.abstractmethod
    def deserialize_guild_unavailable_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.GuildUnavailableEvent:
        """Parse a raw payload from Discord into a guild unavailable event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.GuildUnavailableEvent
            The parsed guild unavailable event object.
        """

    @abc.abstractmethod
    def deserialize_guild_ban_add_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.BanCreateEvent:
        """Parse a raw payload from Discord into a guild ban add event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.BanCreateEvent
            The parsed guild ban add event object.
        """

    @abc.abstractmethod
    def deserialize_guild_ban_remove_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.BanDeleteEvent:
        """Parse a raw payload from Discord into a guild ban remove event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.BanDeleteEvent
            The parsed guild ban remove event object.
        """

    @abc.abstractmethod
    def deserialize_guild_emojis_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_emojis: typing.Sequence[emojis_models.KnownCustomEmoji] | None = None,
    ) -> guild_events.EmojisUpdateEvent:
        """Parse a raw payload from Discord into a guild emojis update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_emojis
            The sequence of emojis or [`None`][].

        Returns
        -------
        hikari.events.guild_events.EmojisUpdateEvent
            The parsed guild emojis update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_stickers_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_stickers: typing.Sequence[sticker_models.GuildSticker] | None = None,
    ) -> guild_events.StickersUpdateEvent:
        """Parse a raw payload from Discord into a guild stickers update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_stickers
            The sequence of stickers or [`None`][].

        Returns
        -------
        hikari.events.guild_events.StickersUpdateEvent
            The parsed guild stickers update event object.
        """

    @abc.abstractmethod
    def deserialize_integration_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.IntegrationCreateEvent:
        """Parse a raw payload from Discord into an integration create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.IntegrationCreateEvent
            The parsed integration create event object.
        """

    @abc.abstractmethod
    def deserialize_integration_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.IntegrationDeleteEvent:
        """Parse a raw payload from Discord into an integration delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.IntegrationDeleteEvent
            The parsed integration delete event object.
        """

    @abc.abstractmethod
    def deserialize_integration_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.IntegrationUpdateEvent:
        """Parse a raw payload from Discord into an integration update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.IntegrationUpdateEvent
            The parsed integration update event object.
        """

    @abc.abstractmethod
    def deserialize_presence_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_presence: presences_models.MemberPresence | None = None,
    ) -> guild_events.PresenceUpdateEvent:
        """Parse a raw payload from Discord into a presence update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_presence
            The presence object or [`None`][].

        Returns
        -------
        hikari.events.guild_events.PresenceUpdateEvent
            The parsed presence update event object.
        """

    @abc.abstractmethod
    def deserialize_audit_log_entry_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> guild_events.AuditLogEntryCreateEvent:
        """Parse a raw payload from Discord into a audit log entry create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.guild_events.AuditLogEntryCreateEvent
            The parsed audit log entry create object.
        """

    ######################
    # INTERACTION EVENTS #
    ######################

    @abc.abstractmethod
    def deserialize_interaction_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> interaction_events.InteractionCreateEvent:
        """Parse a raw payload from Discord into a interaction create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.interaction_events.InteractionCreateEvent
            The parsed interaction create event object.
        """

    #################
    # MEMBER EVENTS #
    #################

    @abc.abstractmethod
    def deserialize_guild_member_add_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> member_events.MemberCreateEvent:
        """Parse a raw payload from Discord into a guild member add event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.member_events.MemberCreateEvent
            The parsed guild member add event object.
        """

    @abc.abstractmethod
    def deserialize_guild_member_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_member: guild_models.Member | None = None,
    ) -> member_events.MemberUpdateEvent:
        """Parse a raw payload from Discord into a guild member update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_member
            The member object or [`None`][].

        Returns
        -------
        hikari.events.member_events.MemberUpdateEvent
            The parsed guild member update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_member_remove_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_member: guild_models.Member | None = None,
    ) -> member_events.MemberDeleteEvent:
        """Parse a raw payload from Discord into a guild member remove event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_member
            The member object or [`None`][].

        Returns
        -------
        hikari.events.member_events.MemberDeleteEvent
            The parsed guild member remove event object.
        """

    ###############
    # ROLE EVENTS #
    ###############

    @abc.abstractmethod
    def deserialize_guild_role_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> role_events.RoleCreateEvent:
        """Parse a raw payload from Discord into a guild role create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.role_events.RoleCreateEvent
            The parsed guild role create event object.
        """

    @abc.abstractmethod
    def deserialize_guild_role_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_role: guild_models.Role | None = None,
    ) -> role_events.RoleUpdateEvent:
        """Parse a raw payload from Discord into a guild role update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_role
            The role object or [`None`][].

        Returns
        -------
        hikari.events.role_events.RoleUpdateEvent
            The parsed guild role update event object.
        """

    @abc.abstractmethod
    def deserialize_guild_role_delete_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_role: guild_models.Role | None = None,
    ) -> role_events.RoleDeleteEvent:
        """Parse a raw payload from Discord into a guild role delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_role
            The role object or [`None`][].

        Returns
        -------
        hikari.events.role_events.RoleDeleteEvent
            The parsed guild role delete event object.
        """

    ##########################
    # SCHEDULED EVENT EVENTS #
    ##########################

    @abc.abstractmethod
    def deserialize_scheduled_event_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> scheduled_events.ScheduledEventCreateEvent:
        """Parse a raw payload from Discord into a scheduled event create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.scheduled_events.ScheduledEventCreateEvent
            The parsed scheduled event create event object.
        """

    @abc.abstractmethod
    def deserialize_scheduled_event_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> scheduled_events.ScheduledEventUpdateEvent:
        """Parse a raw payload from Discord into a scheduled event update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.scheduled_events.ScheduledEventUpdateEvent
            The parsed scheduled event update event object.
        """

    @abc.abstractmethod
    def deserialize_scheduled_event_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> scheduled_events.ScheduledEventDeleteEvent:
        """Parse a raw payload from Discord into a scheduled event delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.scheduled_events.ScheduledEventDeleteEvent
            The parsed scheduled event delete event object.
        """

    @abc.abstractmethod
    def deserialize_scheduled_event_user_add_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> scheduled_events.ScheduledEventUserAddEvent:
        """Parse a raw payload from Discord into a scheduled event user add event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.scheduled_events.ScheduledEventUserAddEvent
            The parsed scheduled event user add event object.
        """

    @abc.abstractmethod
    def deserialize_scheduled_event_user_remove_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> scheduled_events.ScheduledEventUserRemoveEvent:
        """Parse a raw payload from Discord into a scheduled event user remove event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.scheduled_events.ScheduledEventUserRemoveEvent
            The parsed scheduled event user remove event object.
        """

    ###################
    # LIFETIME EVENTS #
    ###################

    @abc.abstractmethod
    def deserialize_starting_event(self) -> lifetime_events.StartingEvent:
        """Build a starting event object.

        Returns
        -------
        hikari.events.lifetime_events.StartingEvent
            The built starting event object.
        """

    @abc.abstractmethod
    def deserialize_started_event(self) -> lifetime_events.StartedEvent:
        """Build a started event object.

        Returns
        -------
        hikari.events.lifetime_events.StartingEvent
            The built started event object.
        """

    @abc.abstractmethod
    def deserialize_stopping_event(self) -> lifetime_events.StoppingEvent:
        """Build a starting event object.

        Returns
        -------
        hikari.events.lifetime_events.StartingEvent
            The built starting event object.
        """

    @abc.abstractmethod
    def deserialize_stopped_event(self) -> lifetime_events.StoppedEvent:
        """Build a stopped event object.

        Returns
        -------
        hikari.events.lifetime_events.StartingEvent
            The built starting event object.
        """

    ##################
    # MESSAGE EVENTS #
    ##################

    @abc.abstractmethod
    def deserialize_message_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> message_events.MessageCreateEvent:
        """Parse a raw payload from Discord into a message create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.message_events.MessageCreateEvent
            The parsed message create event object.
        """

    @abc.abstractmethod
    def deserialize_message_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_message: messages_models.PartialMessage | None = None,
    ) -> message_events.MessageUpdateEvent:
        """Parse a raw payload from Discord into a message update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_message
            The message object or [`None`][].

        Returns
        -------
        hikari.events.message_events.MessageUpdateEvent
            The parsed message update event object.
        """

    @abc.abstractmethod
    def deserialize_message_delete_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_message: messages_models.Message | None = None,
    ) -> message_events.MessageDeleteEvent:
        """Parse a raw payload from Discord into a message delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_message
            The old message object.

        Returns
        -------
        hikari.events.message_events.MessageDeleteEvent
            The parsed message delete event object.
        """

    @abc.abstractmethod
    def deserialize_guild_message_delete_bulk_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_messages: typing.Mapping[snowflakes.Snowflake, messages_models.Message] | None = None,
    ) -> message_events.GuildBulkMessageDeleteEvent:
        """Parse a raw payload from Discord into a guild message delete bulk event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_messages
            A mapping of the old message objects.

        Returns
        -------
        hikari.events.message_events.GuildBulkMessageDeleteEvent
            The parsed guild message delete bulk event object.
        """

    ###################
    # REACTION EVENTS #
    ###################

    @abc.abstractmethod
    def deserialize_message_reaction_add_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> reaction_events.ReactionAddEvent:
        """Parse a raw payload from Discord into a message reaction add event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.reaction_events.ReactionAddEvent
            The parsed message reaction add event object.
        """

    @abc.abstractmethod
    def deserialize_message_reaction_remove_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> reaction_events.ReactionDeleteEvent:
        """Parse a raw payload from Discord into a message reaction remove event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.reaction_events.ReactionDeleteEvent
            The parsed message reaction remove event object.
        """

    @abc.abstractmethod
    def deserialize_message_reaction_remove_all_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> reaction_events.ReactionDeleteAllEvent:
        """Parse a raw payload from Discord into a message reaction remove all event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.reaction_events.ReactionDeleteAllEvent
            The parsed message reaction remove all event object.
        """

    @abc.abstractmethod
    def deserialize_message_reaction_remove_emoji_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> reaction_events.ReactionDeleteEmojiEvent:
        """Parse a raw payload from Discord into a message reaction remove emoji event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.reaction_events.ReactionDeleteEmojiEvent
            The parsed message reaction remove emoji event object.
        """

    ################
    # SHARD EVENTS #
    ################

    @abc.abstractmethod
    def deserialize_shard_payload_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject, *, name: str
    ) -> shard_events.ShardPayloadEvent:
        """Parse a raw payload from Discord into a shard payload event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        name
            Name of the event.

        Returns
        -------
        hikari.events.shard_events.ShardPayloadEvent
            The parsed shard payload event object.
        """

    @abc.abstractmethod
    def deserialize_ready_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> shard_events.ShardReadyEvent:
        """Parse a raw payload from Discord into a ready event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.shard_events.ShardReadyEvent
            The parsed ready event object.
        """

    @abc.abstractmethod
    def deserialize_connected_event(self, shard: gateway_shard.GatewayShard) -> shard_events.ShardConnectedEvent:
        """Build a shard connected event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.

        Returns
        -------
        hikari.events.shard_events.ShardReadyEvent
            The built shard connected event object.
        """

    @abc.abstractmethod
    def deserialize_disconnected_event(self, shard: gateway_shard.GatewayShard) -> shard_events.ShardDisconnectedEvent:
        """Build a shard disconnected event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.

        Returns
        -------
        hikari.events.shard_events.ShardReadyEvent
            The built shard disconnected event object.
        """

    @abc.abstractmethod
    def deserialize_resumed_event(self, shard: gateway_shard.GatewayShard) -> shard_events.ShardResumedEvent:
        """Build a shard resumed event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.

        Returns
        -------
        hikari.events.shard_events.ShardReadyEvent
            The built shard resumed event object.
        """

    @abc.abstractmethod
    def deserialize_guild_member_chunk_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> shard_events.MemberChunkEvent:
        """Parse a raw payload from Discord into a member chunk event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.shard_events.MemberChunkEvent
            The parsed member chunk object.
        """

    ###############
    # USER EVENTS #
    ###############

    @abc.abstractmethod
    def deserialize_own_user_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_user: user_models.OwnUser | None = None,
    ) -> user_events.OwnUserUpdateEvent:
        """Parse a raw payload from Discord into a own user update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_user
            The OwnUser object or [`None`][].

        Returns
        -------
        hikari.events.user_events.OwnUserUpdateEvent
            The parsed own user update event object.
        """

    ################
    # VOICE EVENTS #
    ################

    @abc.abstractmethod
    def deserialize_voice_state_update_event(
        self,
        shard: gateway_shard.GatewayShard,
        payload: data_binding.JSONObject,
        *,
        old_state: voices_models.VoiceState | None = None,
    ) -> voice_events.VoiceStateUpdateEvent:
        """Parse a raw payload from Discord into a voice state update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.
        old_state
            The VoiceState object or [`None`][].

        Returns
        -------
        hikari.events.voice_events.VoiceStateUpdateEvent
            The parsed voice state update event object.
        """

    @abc.abstractmethod
    def deserialize_voice_server_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> voice_events.VoiceServerUpdateEvent:
        """Parse a raw payload from Discord into a voice server update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.voice_events.VoiceServerUpdateEvent
            The parsed voice server update event object.
        """

    @abc.abstractmethod
    def deserialize_auto_mod_rule_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> auto_mod_events.AutoModRuleCreateEvent:
        """Parse a raw payload from Discord into an auto-mod rule create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.voice_events.AutoModRuleCreateEvent
            The parsed auto-mod rule create event object.
        """

    @abc.abstractmethod
    def deserialize_auto_mod_rule_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> auto_mod_events.AutoModRuleUpdateEvent:
        """Parse a raw payload from Discord into an auto-mod rule update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.voice_events.AutoModRuleUpdateEvent
            The parsed auto-mod rule update event object.
        """

    @abc.abstractmethod
    def deserialize_auto_mod_rule_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> auto_mod_events.AutoModRuleDeleteEvent:
        """Parse a raw payload from Discord into an auto-mod rule delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.voice_events.AutoModRuleDeleteEvent
            The parsed auto-mod rule delete event object.
        """

    @abc.abstractmethod
    def deserialize_auto_mod_action_execution_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> auto_mod_events.AutoModActionExecutionEvent:
        """Parse a raw payload from Discord into an auto-mod action execution event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.voice_events.AutoModActionExecutionEvent
            The parsed auto-mod action execution event object.
        """

    ##################
    #  MONETIZATION  #
    ##################

    @abc.abstractmethod
    def deserialize_entitlement_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> monetization_events.EntitlementCreateEvent:
        """Parse a raw payload from Discord into a entitlement create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.entitlement_events.EntitlementCreateEvent
            The parsed entitlement create event object.
        """

    @abc.abstractmethod
    def deserialize_entitlement_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> monetization_events.EntitlementDeleteEvent:
        """Parse a raw payload from Discord into a entitlement delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.entitlement_events.EntitlementDeleteEvent
            The parsed entitlement delete event object.
        """

    @abc.abstractmethod
    def deserialize_entitlement_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> monetization_events.EntitlementUpdateEvent:
        """Parse a raw payload from Discord into a entitlement update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.entitlement_events.EntitlementUpdateEvent
            The parsed entitlement update event object.
        """

    #########################
    # STAGE INSTANCE EVENTS #
    #########################

    @abc.abstractmethod
    def deserialize_stage_instance_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> stage_events.StageInstanceCreateEvent:
        """Parse a raw payload from Discord into a stage instance create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.stage_events.StageInstanceCreateEvent
            The parsed stage instance create event object.
        """

    @abc.abstractmethod
    def deserialize_stage_instance_update_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> stage_events.StageInstanceUpdateEvent:
        """Parse a raw payload from Discord into a stage instance update event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.stage_events.StageInstanceUpdateEvent
            The parsed stage instance update event object.
        """

    @abc.abstractmethod
    def deserialize_stage_instance_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> stage_events.StageInstanceDeleteEvent:
        """Parse a raw payload from Discord into a stage instance delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.stage_events.StageInstanceDeleteEvent
            The parsed stage instance delete event object.
        """

    ################
    #  POLL EVENTS #
    ################

    @abc.abstractmethod
    def deserialize_poll_vote_create_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> poll_events.PollVoteCreateEvent:
        """Parse a raw payload from Discord into a poll vote create event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.poll_events.PollVoteCreateEvent
            The parsed poll vote create event object.
        """

    @abc.abstractmethod
    def deserialize_poll_vote_delete_event(
        self, shard: gateway_shard.GatewayShard, payload: data_binding.JSONObject
    ) -> poll_events.PollVoteDeleteEvent:
        """Parse a raw payload from Discord into a poll vote delete event object.

        Parameters
        ----------
        shard
            The shard that emitted this event.
        payload
            The dict payload to parse.

        Returns
        -------
        hikari.events.poll_events.PollVoteDeleteEvent
            The parsed poll vote delete event object.
        """
