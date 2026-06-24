import { Navigate, Route, Routes } from "react-router-dom";
import Shell from "./components/Shell";
import NationalMap from "./views/NationalMap";
import StatePortfolio from "./views/StatePortfolio";
import PlantDetail from "./views/PlantDetail";

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<NationalMap />} />
        <Route path="/state/:code" element={<StatePortfolio />} />
        <Route path="/plant/:id" element={<PlantDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
