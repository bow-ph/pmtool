// Project Analysis Types
export interface Task {
  id?: number;
  description: string;
  estimated_hours: number;
  actual_hours?: number;
  status: 'pending' | 'in_progress' | 'completed';
  confidence_score: number;
}

export interface PdfAnalysisResponse {
  status: string;
  tasks: Task[];
  total_estimated_hours: number;
  risk_factors: string[];
}

export interface FinancialImpact {
  risk_level: 'low' | 'medium' | 'high';
  potential_cost_overrun: number;
  confidence: number;
}

export interface TimeImpact {
  risk_level: 'low' | 'medium' | 'high';
  potential_delay_hours: number;
  confidence: number;
}

export interface Recommendation {
  type: 'cost' | 'time' | 'resource';
  description: string;
  priority: 'low' | 'medium' | 'high';
}

export interface ProactiveHintsResponse {
  status: string;
  financial_impact: FinancialImpact;
  time_impact: TimeImpact;
  recommendations: Recommendation[];
  time_validation?: {
    validated_tasks: Array<{
      task_id: string;
      original_estimate: number;
      suggested_estimate: number;
      confidence: number;
      adjustment_reason: string;
    }>;
    overall_assessment: {
      estimation_quality: 'good' | 'needs_review' | 'poor';
      suggestions: string[];
    };
  };
}

// Package Types
export interface Package {
  id: number;
  name: string;
  description: string;
  price: number;
  button_text: string;
  features: string[];
}

// CalDAV Types
export interface CalDAVTask {
  uid: string;
  description: string;
  start_date: string;
  end_date: string;
  estimated_hours: number;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
}

export interface CalDAVResponse {
  tasks: CalDAVTask[];
  caldav_url: string;
}
