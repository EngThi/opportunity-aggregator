import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import asyncio
import discord

# Add src and bot root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add src to path explicitly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock database imports to prevent creating test dbs during module load
import database
database.DB_PATH = "test_bot_opportunities.db"

# Now we can import bot
import bot

class TestDiscordBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Prevent discord logic from executing external calls
        bot.validate_env = MagicMock(return_value=True)

    async def asyncTearDown(self):
        if os.path.exists("test_bot_opportunities.db"):
            os.remove("test_bot_opportunities.db")

    @patch('bot.fetch_top_opportunities_sync')
    async def test_opportunities_cmd(self, mock_fetch):
        # Mock what the background task would return
        mock_fetch.return_value = [
            {'title': 'Oportunidade Top', 'score': 90, 'rationale': 'Great match.', 'source': 'Test', 'url': 'http://test'}
        ]

        # Create mock interaction
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()

        # Run command
        await bot.opportunities_cmd.callback(interaction)

        # Asserts
        interaction.response.defer.assert_awaited_once_with(thinking=True)

        # Ensure followup.send was called
        interaction.followup.send.assert_awaited_once()

        # Verify the embed is built properly
        args, kwargs = interaction.followup.send.call_args
        self.assertIn('embed', kwargs)
        embed = kwargs['embed']
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.title, "🚀 Top Opportunites for You")
        self.assertEqual(len(embed.fields), 1)
        self.assertIn("Oportunidade Top", embed.fields[0].name)

    async def test_opportunities_cmd_empty(self):
        with patch('bot.fetch_top_opportunities_sync', return_value=[]):
            interaction = AsyncMock(spec=discord.Interaction)
            interaction.response = AsyncMock()
            interaction.followup = AsyncMock()

            await bot.opportunities_cmd.callback(interaction)
            interaction.response.defer.assert_awaited_once()
            interaction.followup.send.assert_awaited_once_with("⚠️ Nenhuma oportunidade disponível no momento.")

    @patch('scorer.AIScorer.score_opportunity')
    async def test_analyze_cmd(self, mock_score):
        mock_score.return_value = (85, 'Fallback Rationale')

        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()

        text_to_analyze = "Vaga de estagio em Python e Machine Learning"
        await bot.analyze_cmd.callback(interaction, text=text_to_analyze)

        interaction.response.defer.assert_awaited_once()
        interaction.followup.send.assert_awaited_once()

        args, kwargs = interaction.followup.send.call_args
        self.assertIn('embed', kwargs)
        embed = kwargs['embed']
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.title, "🧠 Match Analysis")

        # Find score and rationale fields
        field_names = [field.name for field in embed.fields]
        self.assertIn("Score", field_names)
        self.assertIn("Veredito", field_names)

if __name__ == '__main__':
    unittest.main()
