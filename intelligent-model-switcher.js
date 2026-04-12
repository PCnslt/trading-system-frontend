// Intelligent Model Switcher for OpenClaw
// Analyzes prompt context and switches between DeepSeek Reasoner and DeepSeek Chat

class ModelSwitcher {
  constructor() {
    this.currentModel = 'deepseek/deepseek-chat'; // Default
    this.reasonerKeywords = [
      // Coding & Development
      'code', 'coding', 'program', 'develop', 'build', 'fix', 'error', 'bug',
      'TypeScript', 'Angular', 'compile', 'syntax', 'function', 'class', 'interface',
      'component', 'service', 'module', 'import', 'export', 'debug', 'test',
      'implement', 'algorithm', 'logic', 'complex', 'analysis', 'design',
      'architecture', 'refactor', 'optimize', 'performance', 'memory', 'storage',
      'database', 'API', 'endpoint', 'backend', 'frontend', 'infrastructure',
      'docker', 'container', 'port', 'configuration', 'setup', 'install',
      'dependency', 'package.json', 'tsconfig', 'angular.json', 'build',
      'deploy', 'CI/CD', 'git', 'commit', 'push', 'merge', 'branch', 'repository',
      
      // System & Technical
      'system', 'technical', 'troubleshoot', 'issue', 'problem', 'diagnose',
      'monitor', 'log', 'trace', 'profile', 'benchmark', 'scale', 'load',
      'security', 'auth', 'authentication', 'encryption', 'SSL', 'TLS',
      'network', 'protocol', 'socket', 'WebSocket', 'REST', 'GraphQL',
      
      // Complex Analysis
      'analyze', 'review', 'audit', 'evaluate', 'assess', 'compare', 'contrast',
      'strategize', 'plan', 'roadmap', 'architecture', 'design pattern',
      'framework', 'library', 'SDK', 'API', 'integration', 'migration',
      
      // Math & Logic
      'calculate', 'compute', 'algorithm', 'formula', 'equation', 'statistics',
      'probability', 'regression', 'correlation', 'optimization', 'maximize',
      'minimize', 'constraint', 'variable', 'parameter', 'function', 'method'
    ];
    
    this.chatKeywords = [
      // Simple Conversations
      'hi', 'hello', 'hey', 'thanks', 'thank you', 'ok', 'okay', 'yes', 'no',
      'maybe', 'perhaps', 'possibly', 'probably', 'sure', 'certainly',
      
      // Status & Updates
      'status', 'progress', 'update', 'report', 'check', 'verify', 'confirm',
      'done', 'complete', 'finished', 'ready', 'available', 'working',
      
      // Brief Questions
      'what', 'when', 'where', 'how', 'why', 'who', 'which', 'whose', 'whom',
      'can', 'could', 'would', 'should', 'may', 'might', 'must', 'shall',
      
      // General Chat
      'weather', 'time', 'date', 'day', 'week', 'month', 'year', 'today',
      'tomorrow', 'yesterday', 'now', 'later', 'soon', 'recently', 'previously'
    ];
  }
  
  analyzePrompt(prompt) {
    const lowerPrompt = prompt.toLowerCase();
    let reasonerScore = 0;
    let chatScore = 0;
    
    // Check for reasoner keywords
    for (const keyword of this.reasonerKeywords) {
      if (lowerPrompt.includes(keyword.toLowerCase())) {
        reasonerScore += 2; // Higher weight for technical keywords
      }
    }
    
    // Check for chat keywords
    for (const keyword of this.chatKeywords) {
      if (lowerPrompt.includes(keyword.toLowerCase())) {
        chatScore += 1;
      }
    }
    
    // Check prompt length (short prompts likely chat)
    if (prompt.length < 50) {
      chatScore += 2;
    }
    
    // Check for question marks (simple questions)
    const questionCount = (prompt.match(/\?/g) || []).length;
    if (questionCount > 0 && prompt.length < 100) {
      chatScore += questionCount;
    }
    
    // Check for exclamation marks (emotional/chatty)
    const exclamationCount = (prompt.match(/\!/g) || []).length;
    if (exclamationCount > 0) {
      chatScore += exclamationCount;
    }
    
    // Check for code blocks or technical formatting
    if (prompt.includes('```') || prompt.includes('function') || prompt.includes('class ') || prompt.includes('import ')) {
      reasonerScore += 5;
    }
    
    return { reasonerScore, chatScore };
  }
  
  shouldSwitchToReasoner(prompt) {
    const scores = this.analyzePrompt(prompt);
    
    // If reasoner score is significantly higher, switch
    if (scores.reasonerScore > scores.chatScore * 1.5) {
      return true;
    }
    
    // If prompt contains multiple technical keywords
    if (scores.reasonerScore >= 4) {
      return true;
    }
    
    // If prompt is long and complex
    if (prompt.length > 200 && scores.reasonerScore > 0) {
      return true;
    }
    
    return false;
  }
  
  shouldSwitchToChat(prompt) {
    const scores = this.analyzePrompt(prompt);
    
    // If chat score is higher and reasoner score is low
    if (scores.chatScore > scores.reasonerScore && scores.reasonerScore < 2) {
      return true;
    }
    
    // If prompt is very short
    if (prompt.length < 30) {
      return true;
    }
    
    // If it's a simple greeting or status check
    const lowerPrompt = prompt.toLowerCase();
    if (lowerPrompt.startsWith('hi ') || lowerPrompt.startsWith('hello ') || 
        lowerPrompt.includes('how are you') || lowerPrompt.includes('status')) {
      return true;
    }
    
    return false;
  }
  
  getRecommendedModel(prompt) {
    if (this.shouldSwitchToReasoner(prompt)) {
      return 'deepseek/deepseek-reasoner';
    } else if (this.shouldSwitchToChat(prompt)) {
      return 'deepseek/deepseek-chat';
    }
    
    // Default to current model
    return this.currentModel;
  }
  
  switchModel(prompt) {
    const recommendedModel = this.getRecommendedModel(prompt);
    
    if (recommendedModel !== this.currentModel) {
      console.log(`Switching from ${this.currentModel} to ${recommendedModel}`);
      console.log(`Reason: ${this.getSwitchReason(prompt)}`);
      this.currentModel = recommendedModel;
      return true;
    }
    
    return false;
  }
  
  getSwitchReason(prompt) {
    const scores = this.analyzePrompt(prompt);
    
    if (this.shouldSwitchToReasoner(prompt)) {
      return `Technical/coding task detected (Reasoner score: ${scores.reasonerScore}, Chat score: ${scores.chatScore})`;
    } else if (this.shouldSwitchToChat(prompt)) {
      return `Simple conversation detected (Reasoner score: ${scores.reasonerScore}, Chat score: ${scores.chatScore})`;
    }
    
    return `No switch needed (Reasoner score: ${scores.reasonerScore}, Chat score: ${scores.chatScore})`;
  }
}

// Example usage:
const switcher = new ModelSwitcher();

// Test cases
const testPrompts = [
  "Fix the Angular compilation errors in the frontend",
  "Hi, how are you doing today?",
  "Implement a function to calculate Fibonacci sequence",
  "What's the status of the backend server?",
  "Analyze the performance bottlenecks in the database queries",
  "Thanks for your help!",
  "Create a Docker container configuration for the Spring Boot application",
  "Can you check if the API is working?",
  "Debug the WebSocket connection issue on port 8082",
  "Hello! Just checking in."
];

console.log("=== Model Switcher Test Results ===\n");
for (const prompt of testPrompts) {
  const recommended = switcher.getRecommendedModel(prompt);
  const reason = switcher.getSwitchReason(prompt);
  console.log(`Prompt: "${prompt}"`);
  console.log(`Recommended: ${recommended}`);
  console.log(`Reason: ${reason}`);
  console.log('---');
}

module.exports = ModelSwitcher;