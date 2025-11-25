import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import BudgetCreator from './components/BudgetCreator';
import BudgetList from './components/BudgetList';
import ConstructionManager from './components/ConstructionManager';
import { ViewState, Budget } from './types';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewState>(ViewState.CREATE_BUDGET);
  const [savedBudgets, setSavedBudgets] = useState<Budget[]>([]);
  const [activeBudget, setActiveBudget] = useState<Budget | null>(null);

  const handleSaveBudget = (budget: Budget) => {
    setSavedBudgets([...savedBudgets, budget]);
    // Optional: Switch to list view automatically
    // setCurrentView(ViewState.SAVED_BUDGETS);
  };

  const handleSelectBudget = (budget: Budget) => {
    setActiveBudget(budget);
    setCurrentView(ViewState.GEN_OBRAS);
  };

  const handleDeleteBudget = (id: string) => {
    setSavedBudgets(savedBudgets.filter(b => b.id !== id));
    if (activeBudget?.id === id) {
        setActiveBudget(null);
    }
  };

  return (
    <div className="flex h-screen bg-azure-950 text-slate-200 font-sans selection:bg-cyan-500/30">
      <Sidebar currentView={currentView} onChangeView={setCurrentView} />
      
      <main className="flex-1 overflow-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-azure-900 via-azure-950 to-black">
        <div className="max-w-7xl mx-auto p-8 min-h-full">
          {currentView === ViewState.CREATE_BUDGET && (
            <BudgetCreator onSave={handleSaveBudget} />
          )}
          
          {currentView === ViewState.SAVED_BUDGETS && (
            <BudgetList 
                budgets={savedBudgets} 
                onSelect={handleSelectBudget}
                onDelete={handleDeleteBudget}
            />
          )}
          
          {currentView === ViewState.GEN_OBRAS && (
            <ConstructionManager activeBudget={activeBudget} />
          )}
        </div>
      </main>
    </div>
  );
};

export default App;