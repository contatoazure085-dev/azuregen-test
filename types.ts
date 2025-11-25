export enum ViewState {
  CREATE_BUDGET = 'CREATE_BUDGET',
  SAVED_BUDGETS = 'SAVED_BUDGETS',
  GEN_OBRAS = 'GEN_OBRAS'
}

export interface BudgetItem {
  id: string;
  description: string;
  unit: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  source: 'Manual' | 'SEINFRA-CE' | 'Mercado-Fortal' | 'Otimizado';
  notes?: string;
}

export interface Budget {
  id: string;
  name: string;
  date: string;
  items: BudgetItem[];
  totalValue: number;
}

export interface ScheduleTask {
  id: string;
  name: string;
  startWeek: number;
  durationWeeks: number;
  progress: number;
}

export interface FinancialPoint {
  week: number;
  projectedCost: number;
  actualCost: number;
}

export interface ProjectPlan {
  schedule: ScheduleTask[];
  financials: FinancialPoint[];
  riskAnalysis: string;
}