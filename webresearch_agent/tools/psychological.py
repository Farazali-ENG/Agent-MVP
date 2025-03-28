from typing import Dict, List, Optional
from langchain.tools import BaseTool
from textblob import TextBlob
import re
import json
from collections import Counter
from pydantic import Field
from duckduckgo_search import DDGS

class WebSearchTool(BaseTool):
    """Search the web for information about a company or topic"""
    name: str = Field(default="web_search")
    description: str = Field(default="Search the web for information")

    def _run(self, query: str) -> str:
        """Search the web using DuckDuckGo"""
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=5):
                    results.append(f"Title: {r['title']}\nLink: {r['link']}\nSnippet: {r['body']}\n")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async implementation of web search"""
        return self._run(query)  # DuckDuckGo doesn't have async API, so we just wrap sync version

class EmotionalLanguageAnalyzer(BaseTool):
    """Analyzes emotional language and sentiment patterns in text"""
    name: str = Field(default="emotional_language_analyzer")
    description: str = Field(default="Analyzes emotional content and sentiment in text")
    emotion_keywords: Dict[str, List[str]] = Field(default_factory=lambda: {
        'fear': ['worry', 'risk', 'danger', 'concern', 'scary', 'afraid', 'uncertain'],
        'desire': ['want', 'need', 'wish', 'hope', 'dream', 'aspire', 'goal'],
        'trust': ['reliable', 'secure', 'safe', 'proven', 'trusted', 'confident', 'assured'],
        'frustration': ['difficult', 'annoying', 'complex', 'challenging', 'frustrating', 'problem'],
        'relief': ['solution', 'solve', 'help', 'easy', 'simple', 'quick', 'effortless'],
        'achievement': ['success', 'accomplish', 'achieve', 'win', 'improve', 'grow', 'excel']
    })

    def _run(self, text: str) -> Dict:
        """Analyze emotional content in text"""
        # Sentiment analysis
        blob = TextBlob(text.lower())
        sentiment = blob.sentiment

        # Emotion detection
        emotion_counts = {emotion: 0 for emotion in self.emotion_keywords}
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                emotion_counts[emotion] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            },
            "emotion_distribution": emotion_counts,
            "dominant_emotions": sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
    async def _arun(self, text: str) -> Dict:
        """Async implementation of emotional analysis"""
        return self._run(text)

class PersuasionPatternAnalyzer(BaseTool):
    """Analyzes persuasion patterns and techniques in text"""
    name: str = Field(default="persuasion_pattern_analyzer")
    description: str = Field(default="Identifies persuasion techniques and patterns")
    persuasion_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'scarcity': ['limited', 'exclusive', 'only', 'rare', 'running out', 'closing soon'],
        'social_proof': ['others', 'people', 'customers', 'reviews', 'testimonials', 'popular'],
        'authority': ['expert', 'research', 'study', 'proven', 'certified', 'professional'],
        'reciprocity': ['free', 'bonus', 'gift', 'extra', 'special offer', 'complimentary'],
        'commitment': ['start', 'join', 'become', 'try', 'get started', 'begin'],
        'liking': ['like', 'love', 'enjoy', 'appreciate', 'prefer', 'favorite']
    })

    def _run(self, text: str) -> Dict:
        """Analyze persuasion patterns in text"""
        pattern_counts = {pattern: 0 for pattern in self.persuasion_patterns}
        for pattern, keywords in self.persuasion_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "pattern_distribution": pattern_counts,
            "dominant_patterns": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
    async def _arun(self, text: str) -> Dict:
        """Async implementation of persuasion analysis"""
        return self._run(text)

class CognitiveBiasAnalyzer(BaseTool):
    """Analyzes text for cognitive biases and decision-making patterns"""
    name: str = Field(default="cognitive_bias_analyzer")
    description: str = Field(default="Identifies cognitive biases and decision patterns")
    cognitive_biases: Dict[str, List[str]] = Field(default_factory=lambda: {
        'anchoring': ['compare', 'normally', 'usually', 'typically', 'standard', 'benchmark'],
        'loss_aversion': ['lose', 'miss out', 'risk', 'waste', 'save', 'protect'],
        'bandwagon': ['everyone', 'popular', 'trending', 'common', 'standard', 'normal'],
        'framing': ['better', 'best', 'worse', 'worst', 'more', 'less'],
        'confirmation': ['prove', 'confirm', 'validate', 'right', 'correct', 'true'],
        'availability': ['easily', 'quickly', 'remember', 'recent', 'latest', 'now']
    })

    def _run(self, text: str) -> Dict:
        """Analyze cognitive biases in text"""
        bias_counts = {bias: 0 for bias in self.cognitive_biases}
        for bias, keywords in self.cognitive_biases.items():
            for keyword in keywords:
                bias_counts[bias] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "bias_distribution": bias_counts,
            "dominant_biases": sorted(bias_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
    async def _arun(self, text: str) -> Dict:
        """Async implementation of cognitive bias analysis"""
        return self._run(text)

class NeuroPricingAnalyzer(BaseTool):
    """Analyzes pricing psychology and value perception patterns"""
    name: str = Field(default="neuro_pricing_analyzer")
    description: str = Field(default="Analyzes pricing psychology and value perception")
    pricing_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'anchoring': [r'\$\d+\.99', 'regular price', 'normally', 'originally'],
        'value_focus': ['worth', 'value', 'save', 'discount', 'offer'],
        'scarcity': ['limited time', 'special price', 'exclusive rate'],
        'comparison': ['cheaper', 'better value', 'best price', 'competitive'],
        'bundling': ['package', 'bundle', 'included', 'bonus', 'additional'],
        'prestige': ['premium', 'luxury', 'exclusive', 'high-end', 'elite']
    })

    def _run(self, text: str) -> Dict:
        """Analyze pricing psychology in text"""
        pattern_counts = {pattern: 0 for pattern in self.pricing_patterns}
        for pattern, keywords in self.pricing_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        # Price point analysis
        price_points = re.findall(r'\$\d+(?:\.\d{2})?', text)
        
        return {
            "pricing_patterns": pattern_counts,
            "dominant_patterns": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "price_points_found": price_points,
            "price_positioning": self._analyze_price_positioning(text, price_points)
        }

    def _analyze_price_positioning(self, text: str, price_points: List[str]) -> str:
        if not price_points:
            return "No explicit pricing found"
        
        # Analyze context around price points
        value_words = len(re.findall(r'\b(value|worth|save|discount)\b', text.lower()))
        premium_words = len(re.findall(r'\b(premium|luxury|exclusive)\b', text.lower()))
        
        if premium_words > value_words:
            return "Premium positioning"
        elif value_words > premium_words:
            return "Value-focused positioning"
        else:
            return "Neutral positioning"
            
    async def _arun(self, text: str) -> Dict:
        """Async implementation of pricing psychology analysis"""
        return self._run(text)

class UserIntentAnalyzer(BaseTool):
    """Analyzes user intent and motivation patterns"""
    name: str = Field(default="user_intent_analyzer")
    description: str = Field(default="Analyzes user intent and motivation patterns")
    intent_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'information_seeking': ['how', 'what', 'why', 'when', 'learn', 'understand'],
        'problem_solving': ['solve', 'fix', 'help', 'improve', 'solution'],
        'comparison': ['compare', 'difference', 'better', 'best', 'versus'],
        'purchase_ready': ['buy', 'price', 'cost', 'purchase', 'order'],
        'research': ['research', 'review', 'evaluate', 'assess', 'analyze'],
        'support': ['help', 'support', 'assist', 'guide', 'explain']
    })

    def _run(self, text: str) -> Dict:
        """Analyze user intent in text"""
        intent_counts = {intent: 0 for intent in self.intent_patterns}
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                intent_counts[intent] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        # Analyze question patterns
        questions = len(re.findall(r'\?', text))
        
        return {
            "intent_distribution": intent_counts,
            "dominant_intents": sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "question_frequency": questions,
            "engagement_level": self._analyze_engagement_level(text, questions, intent_counts)
        }

    def _analyze_engagement_level(self, text: str, questions: int, intent_counts: Dict) -> str:
        total_intent_signals = sum(intent_counts.values())
        words = len(text.split())
        
        signal_density = total_intent_signals / words if words > 0 else 0
        
        if signal_density > 0.1 and questions > 2:
            return "High engagement"
        elif signal_density > 0.05 or questions > 0:
            return "Medium engagement"
        else:
            return "Low engagement"
            
    async def _arun(self, text: str) -> Dict:
        """Async implementation of user intent analysis"""
        return self._run(text)

class SocialInfluenceAnalyzer(BaseTool):
    """Analyzes social influence and credibility signals in text"""
    name: str = Field(default="social_influence_analyzer")
    description: str = Field(default="Identifies social influence and credibility patterns")
    influence_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'social_proof': ['testimonials', 'reviews', 'ratings', 'customers', 'clients', 'users'],
        'authority': ['expert', 'certified', 'professional', 'licensed', 'qualified', 'experienced'],
        'credibility': ['trusted', 'proven', 'reliable', 'established', 'recognized', 'accredited'],
        'reputation': ['known', 'leading', 'respected', 'recommended', 'preferred', 'chosen'],
        'engagement': ['community', 'followers', 'network', 'partners', 'members', 'audience'],
        'trust': ['guarantee', 'warranty', 'promise', 'commitment', 'assurance', 'satisfaction']
    })

    def _run(self, text: str) -> Dict:
        """Analyze social influence patterns in text"""
        pattern_counts = {pattern: 0 for pattern in self.influence_patterns}
        for pattern, keywords in self.influence_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "influence_distribution": pattern_counts,
            "dominant_patterns": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "social_signals": self._analyze_social_signals(text)
        }

    def _analyze_social_signals(self, text: str) -> Dict:
        """Analyze specific social proof signals"""
        # Look for numeric social proof
        numbers = re.findall(r'\d+(?:,\d{3})*(?:\+)?(?:\s*(?:customers?|clients?|users?|reviews?|years?))?', text.lower())
        
        # Look for trust indicators
        trust_indicators = re.findall(r'\b(?:certified|licensed|accredited|guaranteed|trusted|proven)\b', text.lower())
        
        return {
            "numeric_proof": numbers,
            "trust_indicators": trust_indicators,
            "credibility_level": self._assess_credibility_level(numbers, trust_indicators)
        }

    def _assess_credibility_level(self, numbers: List[str], trust_indicators: List[str]) -> str:
        """Assess overall credibility level based on signals"""
        score = len(numbers) + len(trust_indicators)
        
        if score > 5:
            return "high"
        elif score > 2:
            return "medium"
        else:
            return "low"
            
    async def _arun(self, text: str) -> Dict:
        """Async implementation of social influence analysis"""
        return self._run(text)

class TrustSignalAnalyzer(BaseTool):
    """Analyzes trust signals and credibility indicators in text"""
    name: str = Field(default="trust_signal_analyzer")
    description: str = Field(default="Identifies trust-building elements and credibility signals")
    trust_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'credentials': ['certified', 'licensed', 'accredited', 'registered', 'authorized', 'qualified'],
        'experience': ['years', 'established', 'since', 'experience', 'track record', 'history'],
        'guarantees': ['guarantee', 'warranty', 'promise', 'assured', 'satisfaction', 'money-back'],
        'security': ['secure', 'protected', 'safe', 'confidential', 'privacy', 'encrypted'],
        'recognition': ['award', 'rated', 'featured', 'recognized', 'acclaimed', 'honored'],
        'compliance': ['compliant', 'standards', 'regulations', 'certified', 'approved', 'verified']
    })

    def _run(self, text: str) -> Dict:
        """Analyze trust signals in text"""
        signal_counts = {signal: 0 for signal in self.trust_patterns}
        for signal, keywords in self.trust_patterns.items():
            for keyword in keywords:
                signal_counts[signal] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "trust_distribution": signal_counts,
            "dominant_signals": sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "trust_metrics": self._analyze_trust_metrics(text)
        }

    def _analyze_trust_metrics(self, text: str) -> Dict:
        """Analyze specific trust metrics"""
        # Look for years of experience
        years = re.findall(r'\d+(?:\+)?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|history|service))?', text.lower())
        
        # Look for certifications and credentials
        credentials = re.findall(r'\b(?:certified|licensed|accredited|registered|authorized)\b\s+(?:\w+\s+)*(?:professional|contractor|company|business|expert)', text.lower())
        
        # Look for guarantees
        guarantees = re.findall(r'\b(?:\d+(?:-|\s)?(?:day|year|month)|money[\s-]?back|satisfaction)\s*guarantee\b', text.lower())
        
        return {
            "experience_claims": years,
            "credentials": credentials,
            "guarantees": guarantees,
            "trust_level": self._assess_trust_level(years, credentials, guarantees)
        }

    def _assess_trust_level(self, years: List[str], credentials: List[str], guarantees: List[str]) -> str:
        """Assess overall trust level based on signals"""
        score = len(years) + len(credentials) * 2 + len(guarantees)
        
        if score > 5:
            return "high"
        elif score > 2:
            return "medium"
        else:
            return "low" 

class MarketAnalyzer(BaseTool):
    """Analyzes market positioning and competitive dynamics"""
    name: str = Field(default="market_analyzer")
    description: str = Field(default="Analyzes market positioning and competitive factors")
    market_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'differentiation': ['unique', 'different', 'exclusive', 'only', 'special', 'innovative'],
        'value_prop': ['better', 'faster', 'cheaper', 'easier', 'superior', 'advanced'],
        'market_position': ['leader', 'best', 'top', 'premier', 'preferred', 'chosen'],
        'competition': ['competitor', 'alternative', 'other', 'choice', 'option', 'solution'],
        'target_market': ['ideal for', 'perfect for', 'designed for', 'specialized in', 'focused on'],
        'industry_trends': ['trending', 'growing', 'emerging', 'innovative', 'cutting-edge', 'modern']
    })

    def _run(self, text: str) -> Dict:
        """Analyze market positioning in text"""
        pattern_counts = {pattern: 0 for pattern in self.market_patterns}
        for pattern, keywords in self.market_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "market_signals": pattern_counts,
            "dominant_signals": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "positioning_analysis": self._analyze_positioning(text)
        }

    def _analyze_positioning(self, text: str) -> Dict:
        """Analyze specific market positioning elements"""
        # Look for comparative statements
        comparisons = re.findall(r'\b(?:better|best|faster|easier|more|most)\s+(?:than|in|of|on)\b', text.lower())
        
        # Look for target market specifications
        target_specs = re.findall(r'\b(?:ideal|perfect|designed|specialized|focused)\s+for\s+(?:\w+\s+)*(?:businesses?|companies?|industries?|customers?|clients?)', text.lower())
        
        # Look for unique value propositions
        value_props = re.findall(r'\b(?:unique|exclusive|only|special)\s+(?:\w+\s+)*(?:feature|solution|service|product|offering)', text.lower())
        
        return {
            "comparative_claims": comparisons,
            "target_segments": target_specs,
            "value_propositions": value_props,
            "positioning_strength": self._assess_positioning_strength(comparisons, target_specs, value_props)
        }

    def _assess_positioning_strength(self, comparisons: List[str], target_specs: List[str], value_props: List[str]) -> str:
        """Assess overall positioning strength"""
        score = len(comparisons) + len(target_specs) * 2 + len(value_props) * 2
        
        if score > 6:
            return "strong"
        elif score > 3:
            return "moderate"
        else:
            return "weak" 

class CompetitorAnalyzer(BaseTool):
    """Analyzes competitive positioning and differentiation"""
    name: str = Field(default="competitor_analyzer")
    description: str = Field(default="Analyzes competitive positioning and differentiation factors")
    competitor_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'comparison': ['versus', 'compared to', 'better than', 'unlike', 'different from', 'instead of'],
        'advantages': ['advantage', 'benefit', 'superior', 'exclusive', 'unique', 'only'],
        'features': ['feature', 'capability', 'functionality', 'offering', 'service', 'solution'],
        'weaknesses': ['limitation', 'drawback', 'problem', 'issue', 'challenge', 'difficulty'],
        'alternatives': ['alternative', 'option', 'choice', 'substitute', 'replacement', 'competitor'],
        'market_gaps': ['missing', 'lacking', 'need', 'gap', 'opportunity', 'demand']
    })

    def _run(self, text: str) -> Dict:
        """Analyze competitive positioning in text"""
        pattern_counts = {pattern: 0 for pattern in self.competitor_patterns}
        for pattern, keywords in self.competitor_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "competitive_signals": pattern_counts,
            "dominant_signals": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "competitive_analysis": self._analyze_competition(text)
        }

    def _analyze_competition(self, text: str) -> Dict:
        """Analyze specific competitive elements"""
        # Look for direct comparisons
        comparisons = re.findall(r'\b(?:better|more|faster|easier|superior)\s+than\s+(?:\w+\s+)*(?:competitors?|alternatives?|others?)', text.lower())
        
        # Look for unique advantages
        advantages = re.findall(r'\b(?:unique|exclusive|only|special)\s+(?:\w+\s+)*(?:advantage|benefit|feature|capability)', text.lower())
        
        # Look for market positioning
        positioning = re.findall(r'\b(?:leader|best|top|premier|preferred)\s+(?:\w+\s+)*(?:provider|company|solution|choice)', text.lower())
        
        return {
            "direct_comparisons": comparisons,
            "unique_advantages": advantages,
            "market_positioning": positioning,
            "competitive_strength": self._assess_competitive_strength(comparisons, advantages, positioning)
        }

    def _assess_competitive_strength(self, comparisons: List[str], advantages: List[str], positioning: List[str]) -> str:
        """Assess overall competitive strength"""
        score = len(comparisons) + len(advantages) * 2 + len(positioning) * 2
        
        if score > 6:
            return "strong"
        elif score > 3:
            return "moderate"
        else:
            return "weak" 

class PositioningAnalyzer(BaseTool):
    """Analyzes market positioning and brand differentiation"""
    name: str = Field(default="positioning_analyzer")
    description: str = Field(default="Analyzes market positioning and brand differentiation")
    positioning_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'brand_identity': ['brand', 'identity', 'reputation', 'known for', 'recognized as', 'established'],
        'value_proposition': ['value', 'benefit', 'advantage', 'solution', 'offering', 'service'],
        'target_audience': ['ideal for', 'perfect for', 'designed for', 'specialized in', 'focused on'],
        'differentiation': ['unique', 'different', 'exclusive', 'only', 'special', 'innovative'],
        'quality_signals': ['premium', 'quality', 'excellence', 'superior', 'best-in-class', 'top-tier'],
        'market_focus': ['market leader', 'industry expert', 'specialist', 'authority', 'preferred']
    })

    def _run(self, text: str) -> Dict:
        """Analyze market positioning in text"""
        pattern_counts = {pattern: 0 for pattern in self.positioning_patterns}
        for pattern, keywords in self.positioning_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "positioning_signals": pattern_counts,
            "dominant_signals": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "positioning_analysis": self._analyze_positioning_elements(text)
        }

    def _analyze_positioning_elements(self, text: str) -> Dict:
        """Analyze specific positioning elements"""
        # Look for brand statements
        brand_statements = re.findall(r'\b(?:we are|our|us)\s+(?:\w+\s+)*(?:leader|expert|specialist|provider|choice)', text.lower())
        
        # Look for value propositions
        value_props = re.findall(r'\b(?:deliver|provide|offer|create|bring)\s+(?:\w+\s+)*(?:value|benefit|solution|advantage)', text.lower())
        
        # Look for differentiation claims
        diff_claims = re.findall(r'\b(?:unique|different|exclusive|only|special)\s+(?:\w+\s+)*(?:approach|solution|service|offering|way)', text.lower())
        
        return {
            "brand_positioning": brand_statements,
            "value_propositions": value_props,
            "differentiation_claims": diff_claims,
            "positioning_clarity": self._assess_positioning_clarity(brand_statements, value_props, diff_claims)
        }

    def _assess_positioning_clarity(self, brand_statements: List[str], value_props: List[str], diff_claims: List[str]) -> str:
        """Assess overall positioning clarity"""
        score = len(brand_statements) + len(value_props) * 2 + len(diff_claims) * 2
        
        if score > 6:
            return "clear"
        elif score > 3:
            return "moderate"
        else:
            return "unclear" 

class TrendAnalyzer(BaseTool):
    """Analyzes industry trends and news patterns"""
    name: str = Field(default="trend_analyzer")
    description: str = Field(default="Analyzes industry trends and news patterns")
    trend_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'growth': ['growing', 'expanding', 'increasing', 'rising', 'emerging', 'booming'],
        'innovation': ['innovative', 'new', 'advanced', 'cutting-edge', 'modern', 'latest'],
        'challenges': ['challenge', 'issue', 'problem', 'concern', 'difficulty', 'obstacle'],
        'opportunities': ['opportunity', 'potential', 'prospect', 'possibility', 'chance', 'opening'],
        'regulation': ['regulation', 'compliance', 'standard', 'requirement', 'law', 'policy'],
        'technology': ['technology', 'digital', 'automated', 'smart', 'connected', 'integrated']
    })

    def _run(self, text: str) -> Dict:
        """Analyze trends in text"""
        pattern_counts = {pattern: 0 for pattern in self.trend_patterns}
        for pattern, keywords in self.trend_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "trend_signals": pattern_counts,
            "dominant_trends": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "trend_analysis": self._analyze_trends(text)
        }

    def _analyze_trends(self, text: str) -> Dict:
        """Analyze specific trend elements"""
        # Look for growth indicators
        growth_indicators = re.findall(r'\b(?:grow(?:ing|th)|increase|rise|expand)\s+(?:by|in|of)?\s*\d*\.?\d+\s*%?', text.lower())
        
        # Look for innovation mentions
        innovation_mentions = re.findall(r'\b(?:new|innovative|advanced)\s+(?:\w+\s+)*(?:technology|solution|approach|method)', text.lower())
        
        # Look for industry changes
        industry_changes = re.findall(r'\b(?:industry|market|sector)\s+(?:change|shift|trend|development)', text.lower())
        
        return {
            "growth_metrics": growth_indicators,
            "innovation_focus": innovation_mentions,
            "industry_changes": industry_changes,
            "trend_impact": self._assess_trend_impact(growth_indicators, innovation_mentions, industry_changes)
        }

    def _assess_trend_impact(self, growth_indicators: List[str], innovation_mentions: List[str], industry_changes: List[str]) -> str:
        """Assess overall trend impact"""
        score = len(growth_indicators) * 2 + len(innovation_mentions) + len(industry_changes)
        
        if score > 5:
            return "significant"
        elif score > 2:
            return "moderate"
        else:
            return "minimal" 

class SentimentAnalyzer(BaseTool):
    """Analyzes sentiment and emotional tone in text"""
    name: str = Field(default="sentiment_analyzer")
    description: str = Field(default="Analyzes sentiment and emotional tone in text")
    sentiment_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'positive': ['excellent', 'great', 'good', 'best', 'amazing', 'wonderful', 'outstanding'],
        'negative': ['poor', 'bad', 'worst', 'terrible', 'awful', 'disappointing', 'frustrating'],
        'neutral': ['average', 'moderate', 'typical', 'standard', 'normal', 'regular', 'common'],
        'strong': ['very', 'extremely', 'highly', 'absolutely', 'definitely', 'certainly'],
        'weak': ['somewhat', 'slightly', 'fairly', 'rather', 'quite', 'relatively'],
        'improvement': ['better', 'improved', 'enhanced', 'upgraded', 'advanced', 'refined']
    })

    def _run(self, text: str) -> Dict:
        """Analyze sentiment in text"""
        pattern_counts = {pattern: 0 for pattern in self.sentiment_patterns}
        for pattern, keywords in self.sentiment_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        # Use TextBlob for additional sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        return {
            "sentiment_signals": pattern_counts,
            "dominant_sentiments": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "sentiment_metrics": {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "overall_tone": self._assess_overall_tone(polarity, pattern_counts)
            },
            "detailed_analysis": self._analyze_sentiment_details(text, pattern_counts)
        }

    def _analyze_sentiment_details(self, text: str, pattern_counts: Dict[str, int]) -> Dict:
        """Analyze detailed sentiment elements"""
        # Look for strong positive statements
        strong_positives = re.findall(r'\b(?:very|extremely|highly)\s+(?:\w+\s+)*(?:good|great|excellent)', text.lower())
        
        # Look for strong negative statements
        strong_negatives = re.findall(r'\b(?:very|extremely|highly)\s+(?:\w+\s+)*(?:bad|poor|terrible)', text.lower())
        
        # Look for improvement statements
        improvements = re.findall(r'\b(?:better|improved|enhanced)\s+(?:than|compared|since|after)', text.lower())
        
        return {
            "strong_positives": strong_positives,
            "strong_negatives": strong_negatives,
            "improvements": improvements,
            "sentiment_balance": self._calculate_sentiment_balance(pattern_counts)
        }

    def _assess_overall_tone(self, polarity: float, pattern_counts: Dict[str, int]) -> str:
        """Assess overall tone based on polarity and pattern counts"""
        positive_score = pattern_counts['positive'] + pattern_counts['strong'] * 0.5
        negative_score = pattern_counts['negative'] + pattern_counts['weak'] * 0.5
        
        # Combine with TextBlob polarity
        final_score = (positive_score - negative_score) * 0.5 + polarity * 0.5
        
        if final_score > 0.3:
            return "positive"
        elif final_score < -0.3:
            return "negative"
        else:
            return "neutral"

    def _calculate_sentiment_balance(self, pattern_counts: Dict[str, int]) -> str:
        """Calculate the balance of positive vs negative sentiment"""
        positive_signals = pattern_counts['positive'] + pattern_counts['strong'] + pattern_counts['improvement']
        negative_signals = pattern_counts['negative'] + pattern_counts['weak']
        
        ratio = positive_signals / (negative_signals + 1)  # Add 1 to avoid division by zero
        
        if ratio > 2:
            return "strongly positive"
        elif ratio > 1:
            return "moderately positive"
        elif ratio > 0.5:
            return "balanced"
        else:
            return "negative leaning" 

class ImpactAnalyzer(BaseTool):
    """Analyzes impact and significance of news and events"""
    name: str = Field(default="impact_analyzer")
    description: str = Field(default="Analyzes impact and significance of news and events")
    impact_patterns: Dict[str, List[str]] = Field(default_factory=lambda: {
        'magnitude': ['major', 'significant', 'substantial', 'considerable', 'extensive', 'dramatic'],
        'scope': ['industry-wide', 'market-wide', 'sector-wide', 'global', 'regional', 'local'],
        'duration': ['long-term', 'short-term', 'temporary', 'permanent', 'ongoing', 'lasting'],
        'urgency': ['immediate', 'urgent', 'critical', 'pressing', 'crucial', 'vital'],
        'relevance': ['relevant', 'important', 'key', 'essential', 'fundamental', 'central'],
        'consequences': ['result', 'effect', 'impact', 'outcome', 'consequence', 'implication']
    })

    def _run(self, text: str) -> Dict:
        """Analyze impact in text"""
        pattern_counts = {pattern: 0 for pattern in self.impact_patterns}
        for pattern, keywords in self.impact_patterns.items():
            for keyword in keywords:
                pattern_counts[pattern] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))

        return {
            "impact_signals": pattern_counts,
            "dominant_signals": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "impact_analysis": self._analyze_impact(text)
        }

    def _analyze_impact(self, text: str) -> Dict:
        """Analyze specific impact elements"""
        # Look for quantitative impact
        quantities = re.findall(r'\b\d+(?:\.\d+)?%?\s*(?:increase|decrease|growth|reduction|change)', text.lower())
        
        # Look for temporal indicators
        temporal = re.findall(r'\b(?:within|in|over|during|for)\s+(?:\d+\s+)?(?:days?|weeks?|months?|years?|quarters?)', text.lower())
        
        # Look for scope indicators
        scope = re.findall(r'\b(?:industry|market|sector|region|area|global|local)\s+(?:wide|level|scale|impact|effect)', text.lower())
        
        return {
            "quantitative_impact": quantities,
            "temporal_scope": temporal,
            "impact_scope": scope,
            "significance_level": self._assess_significance(quantities, temporal, scope)
        }

    def _assess_significance(self, quantities: List[str], temporal: List[str], scope: List[str]) -> str:
        """Assess overall significance of impact"""
        score = len(quantities) * 2 + len(temporal) + len(scope) * 1.5
        
        if score > 7:
            return "high"
        elif score > 3:
            return "medium"
        else:
            return "low" 