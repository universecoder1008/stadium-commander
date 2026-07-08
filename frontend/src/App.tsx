import MainLayout from "./layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import { useSimulation } from "./hooks/useSimulation";

function App() {
  const sim = useSimulation();

  return (
    <MainLayout
      navbarProps={{
        currentPhase: sim.status.current_phase,
        liveMode: sim.liveMode,
        setLiveMode: sim.setLiveMode,
        connectionHealthy: sim.connectionHealthy,
        onRefresh: sim.fetchStatus,
        loading: sim.loading
      }}
    >
      <Dashboard sim={sim} />
    </MainLayout>
  );
}

export default App;
