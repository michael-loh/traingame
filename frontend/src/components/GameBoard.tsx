import React from "react";
import { useGame } from "../context/GameContext";
import { City, Route, RouteColor } from "../types/game";
import { EventType } from "../types/events";

const COLOR_MAP: Record<RouteColor, string> = {
  [RouteColor.RED]: "#f87171",
  [RouteColor.BLUE]: "#60a5fa",
  [RouteColor.GREEN]: "#4ade80",
  [RouteColor.YELLOW]: "#facc15",
  [RouteColor.BLACK]: "#44403c",
  [RouteColor.WHITE]: "#f1f5f9",
  [RouteColor.ORANGE]: "#fb923c",
  [RouteColor.PINK]: "#f472b6",
  [RouteColor.ANY]: "#cbd5e1",
};

export const GameBoard: React.FC = () => {
  const { gameState, sendEvent, playerId } = useGame();

  if (!gameState) return null;

  const { cities, board } = gameState;

  const handleClaimRoute = (routeId: string) => {
    sendEvent(EventType.CLAIM_ROUTE, { route_id: routeId, card_ids: [] });
  };

  return (
    <div className="w-full h-full bg-slate-100 rounded-3xl shadow-inner overflow-hidden relative border border-slate-200">
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Render Routes */}
        {Object.values(board).map((route) => (
          <RouteElement
            key={route.id}
            route={route}
            cityA={cities[route.node_a]}
            cityB={cities[route.node_b]}
            onClaim={handleClaimRoute}
            isPlayersTurn={gameState.turn_order[gameState.current_turn_index] === playerId}
          />
        ))}

        {/* Render Cities */}
        {Object.values(cities).map((city) => (
          <g key={city.id} transform={`translate(${city.x}, ${city.y})`}>
            <circle
              r="1.5"
              className="fill-white stroke-slate-900 stroke-[0.4]"
            />
            <text
              y="3.5"
              textAnchor="middle"
              className="font-black fill-slate-900 pointer-events-none select-none uppercase tracking-tighter"
              style={{ fontSize: '2px' }}
            >
              {city.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};

interface RouteProps {
  route: Route;
  cityA: City;
  cityB: City;
  onClaim: (id: string) => void;
  isPlayersTurn: boolean;
}

const RouteElement: React.FC<RouteProps> = ({ route, cityA, cityB, onClaim, isPlayersTurn }) => {
  const dx = cityB.x - cityA.x;
  const dy = cityB.y - cityA.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);

  const margin = 2.5;
  const availableDistance = distance - margin * 2;
  const segmentGap = 0.4;
  const segmentLength = (availableDistance - (route.length - 1) * segmentGap) / route.length;

  let offset = 0;
  if (route.sibling_id) {
    offset = route.id < route.sibling_id ? 1 : -1;
  }

  const segments = Array.from({ length: route.length }, (_, i) => i);

  return (
    <g
      transform={`translate(${cityA.x}, ${cityA.y}) rotate(${angle})`}
      className={`transition-all duration-300 ${
        route.owner_id ? "opacity-100" : "hover:opacity-100 opacity-60"
      } ${!route.owner_id && isPlayersTurn ? "cursor-pointer" : "cursor-default"}`}
      onClick={() => !route.owner_id && isPlayersTurn && onClaim(route.id)}
    >
      {segments.map((i) => (
        <rect
          key={i}
          x={margin + i * (segmentLength + segmentGap)}
          y={offset - 0.5}
          width={segmentLength}
          height={1}
          rx="0.3"
          style={{
            fill: route.owner_id ? "#0f172a" : COLOR_MAP[route.color],
            stroke: route.owner_id ? "white" : "rgba(0,0,0,0.1)",
            strokeWidth: 0.2,
          }}
        />
      ))}
      {!route.owner_id && (
        <rect
          x={margin}
          y={offset - 2}
          width={availableDistance}
          height={4}
          fill="transparent"
        />
      )}
    </g>
  );
};
