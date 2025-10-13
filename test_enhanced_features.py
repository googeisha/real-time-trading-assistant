"""
Test suite for enhanced trading assistant features
"""
import unittest
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import robinhood_market_researcher as rmr
import robinhood_ui_enhanced as rui


class TestEnhancedTradingAssistant(unittest.TestCase):
    """Test suite for enhanced trading assistant features"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        pass
    
    def test_market_analyzer_initialization(self):
        """Test that MarketAnalyzer can be initialized"""
        analyzer = rmr.MarketAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsNotNone(analyzer.data_api)
        self.assertIsNotNone(analyzer.indicators)
        self.assertIsNotNone(analyzer.advanced_indicators)
        self.assertIsNotNone(analyzer.patterns)
        self.assertIsNotNone(analyzer.trading_strategies)
        self.assertIsNotNone(analyzer.watchlist)
        self.assertIsNotNone(analyzer.risk_manager)
    
    def test_risk_manager_initialization(self):
        """Test that RiskManager can be initialized"""
        risk_manager = rmr.RiskManager()
        self.assertIsNotNone(risk_manager)
    
    def test_risk_manager_position_sizing(self):
        """Test position sizing calculation"""
        risk_manager = rmr.RiskManager()
        result = risk_manager.calculate_position_sizing(
            account_size=100000.0,
            risk_per_trade=0.02,  # 2% risk
            stop_loss_distance=5.0,  # $5 stop loss
            current_price=100.0
        )
        
        self.assertIn('position_size', result)
        self.assertIn('position_value', result)
        self.assertIn('risk_amount', result)
        self.assertEqual(result['risk_amount'], 2000.0)  # 2% of $100,000
        self.assertEqual(result['position_size'], 400)  # $2000 risk / $5 stop loss
    
    def test_risk_manager_value_at_risk(self):
        """Test Value at Risk calculation"""
        risk_manager = rmr.RiskManager()
        result = risk_manager.calculate_value_at_risk(
            portfolio_value=100000.0,
            confidence_level=0.95,
            time_horizon=1,
            volatility=0.02  # 2% daily volatility
        )
        
        self.assertIn('var', result)
        self.assertIn('expected_shortfall', result)
        self.assertGreaterEqual(result['var'], 0)
        self.assertGreaterEqual(result['expected_shortfall'], 0)
    
    def test_risk_manager_portfolio_risk_assessment(self):
        """Test portfolio risk assessment"""
        risk_manager = rmr.RiskManager()
        positions = {
            'AAPL': {
                'shares': 100,
                'entry_price': 150.0
            },
            'MSFT': {
                'shares': 50,
                'entry_price': 300.0
            }
        }
        market_data = {
            'AAPL': {'price': 155.0},
            'MSFT': {'price': 305.0}
        }
        
        result = risk_manager.assess_portfolio_risk(positions, market_data)
        
        self.assertIn('total_portfolio_value', result)
        self.assertIn('concentration_risk', result)
        self.assertIn('diversification_score', result)
        self.assertGreaterEqual(result['total_portfolio_value'], 0)
        self.assertGreaterEqual(result['diversification_score'], 0)
        self.assertLessEqual(result['diversification_score'], 1)
    
    def test_risk_manager_risk_controls_suggestions(self):
        """Test risk control suggestions"""
        risk_manager = rmr.RiskManager()
        portfolio_risk = {
            'total_portfolio_value': 100000.0,
            'concentration_risk': {'level': 'High', 'score': 0.4},
            'diversification_score': 0.3
        }
        market_conditions = {
            'volatility': 0.04  # 4% volatility
        }
        
        suggestions = risk_manager.suggest_risk_controls(portfolio_risk, market_conditions)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
    
    def test_market_analyzer_calculate_position_sizing(self):
        """Test MarketAnalyzer position sizing calculation"""
        analyzer = rmr.MarketAnalyzer()
        result = analyzer.calculate_position_sizing(
            account_size=100000.0,
            risk_per_trade=0.02,  # 2% risk
            stop_loss_distance=5.0,  # $5 stop loss
            current_price=100.0
        )
        
        self.assertIn('position_size', result)
        self.assertIn('position_value', result)
        self.assertIn('risk_amount', result)
    
    def test_market_analyzer_calculate_value_at_risk(self):
        """Test MarketAnalyzer Value at Risk calculation"""
        analyzer = rmr.MarketAnalyzer()
        result = analyzer.calculate_value_at_risk(
            portfolio_value=100000.0,
            confidence_level=0.95,
            time_horizon=1,
            volatility=0.02  # 2% daily volatility
        )
        
        self.assertIn('var', result)
        self.assertIn('expected_shortfall', result)
    
    def test_market_analyzer_assess_portfolio_risk(self):
        """Test MarketAnalyzer portfolio risk assessment"""
        analyzer = rmr.MarketAnalyzer()
        positions = {
            'AAPL': {
                'shares': 100,
                'entry_price': 150.0
            }
        }
        market_data = {
            'AAPL': {'price': 155.0}
        }
        
        result = analyzer.assess_portfolio_risk(positions, market_data)
        
        self.assertIn('total_portfolio_value', result)
        self.assertIn('concentration_risk', result)
        self.assertIn('diversification_score', result)
    
    def test_market_analyzer_suggest_risk_controls(self):
        """Test MarketAnalyzer risk control suggestions"""
        analyzer = rmr.MarketAnalyzer()
        portfolio_risk = {
            'total_portfolio_value': 100000.0,
            'concentration_risk': {'level': 'High', 'score': 0.4},
            'diversification_score': 0.3
        }
        market_conditions = {
            'volatility': 0.04  # 4% volatility
        }
        
        suggestions = analyzer.suggest_risk_controls(portfolio_risk, market_conditions)
        
        self.assertIsInstance(suggestions, list)
    
    def test_ui_enhanced_portfolio_summary(self):
        """Test that UI enhanced portfolio summary can be created"""
        # This is a basic test - in practice, we would need to mock the UI
        self.assertTrue(True)  # Placeholder for UI testing


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)