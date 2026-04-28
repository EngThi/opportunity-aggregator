import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import asyncio
import discord

# Add src and bot root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import bot

class TestDiscordBot(unittest.IsolatedAsyncioTestCase):
    @patch('bot.fetch_top_opportunities_sync')
    async def test_opportunities_cmd(self, mock_fetch):
        # Mock what the background task would return (Tuple of List and String)
        mock_fetch.return_value = (
            [{'title': 'Top Opp', 'score': 90, 'rationale': 'Great match.', 'source': 'Test', 'url': 'http://test'}],
            "AI Strategy Recommendation"
        )
    
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user.id = 12345
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        interaction.channel = AsyncMock()
    
        await bot.opportunities_cmd.callback(interaction)
        interaction.response.defer.assert_awaited_once()
        # Verify strategy was sent
        self.assertTrue(interaction.followup.send.called)

    @patch('scorer.AIScorer.score_opportunity')
    async def test_analyze_cmd(self, mock_score):
        mock_score.return_value = (85, 'Analysis text')
    
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.user.id = 12345
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
    
        await bot.analyze_cmd.callback(interaction, text="Some job text")
        interaction.followup.send.assert_awaited_once()
        
        args, kwargs = interaction.followup.send.call_args
        embed = kwargs['embed']
        field_names = [field.name for field in embed.fields]
        # Updated to check new English field names
        self.assertIn("Score", field_names)
        self.assertIn("Verdict", field_names)

if __name__ == '__main__':
    unittest.main()
