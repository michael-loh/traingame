import React, { useState } from "react";
import { useGame } from "../context/GameContext";
import { EventType } from "../types/events";

export const SetupModal: React.FC = () => {
  const { gameState, playerId, sendEvent } = useGame();
  const [selectedGoalIds, setSelectedGoalIds] = useState<string[]>([]);

  if (!gameState || !playerId) return null;

  const player = gameState.players[playerId];
  if (!player || player.pending_goals.length === 0) return null;

  const toggleGoal = (id: string) => {
    setSelectedGoalIds((prev) =>
      prev.includes(id) ? prev.filter((gid) => gid !== id) : [...prev, id]
    );
  };

  const handleConfirm = () => {
    if (selectedGoalIds.length < 2) {
      alert("Keep at least 2 goals!");
      return;
    }
    sendEvent(EventType.CHOOSE_GOALS, { kept_goal_ids: selectedGoalIds });
  };

  return (
    <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-md flex items-center justify-center z-[200] p-6">
      <div className="bg-white rounded-[2rem] shadow-2xl max-w-sm w-full p-8 flex flex-col gap-6 border border-white/20">
        <div className="text-center">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Initial Goals</h2>
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Select at least 2 cards</p>
        </div>
        
        <div className="flex flex-col gap-3">
          {player.pending_goals.map((goal) => (
            <div
              key={goal.id}
              onClick={() => toggleGoal(goal.id)}
              className={`p-4 rounded-2xl border-2 transition-all cursor-pointer ${
                selectedGoalIds.includes(goal.id)
                  ? "border-indigo-500 bg-indigo-50 shadow-md scale-[1.02]"
                  : "border-slate-100 hover:border-slate-200 bg-slate-50 opacity-70"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="text-xs font-black uppercase tracking-tighter text-slate-900">
                  {goal.node_a} - {goal.node_b}
                </span>
                <span className="text-[10px] font-black bg-white px-2 py-1 rounded-lg shadow-sm">
                  {goal.points}
                </span>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleConfirm}
          disabled={selectedGoalIds.length < 2}
          className="w-full py-4 bg-slate-900 text-white font-black rounded-2xl shadow-xl hover:bg-black disabled:opacity-30 transition-all active:scale-95 uppercase tracking-widest text-xs"
        >
          Confirm ({selectedGoalIds.length})
        </button>
      </div>
    </div>
  );
};
