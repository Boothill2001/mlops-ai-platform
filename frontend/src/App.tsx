import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import OnlineInference from './pages/OnlineInference';
import BatchJobs from './pages/BatchJobs';
import RagAssistant from './pages/RagAssistant';
import Monitoring from './pages/Monitoring';
import Evaluation from './pages/Evaluation';
import Tutorial from './pages/Tutorial';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-slate-900">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/inference" element={<OnlineInference />} />
            <Route path="/batch" element={<BatchJobs />} />
            <Route path="/rag" element={<RagAssistant />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="/tutorial" element={<Tutorial />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
