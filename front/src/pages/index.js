import LogsTable from "../components/LogsTable";
import AttackChart from "../components/AttackChart";
import TitleHeader from "../components/TitleHeader";
import StatsCard from "../components/StatsCard";
import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";

// Helper to format dates consistently
const formatLogs = (logs) => {
  return logs.map((log) => ({
    ...log,
    timestamp: new Date(log.timestamp).toISOString(),
    formattedDate: new Date(log.timestamp).toUTCString()
  }));
};

export const getServerSideProps = async () => {
  const response = await fetch(
    "https://backend.anomala.cc/attack-logs"
  );

  const statsResponse = await fetch(
    "https://backend.anomala.cc/stats"
  );


  //const response = await fetch('http://localhost:3000/api/logs');
  const data = await response.json();
  const formattedLogs = formatLogs(data.logs);

  //const statsResponse = await fetch('http://localhost:3000/api/stats');
  const statsData = await statsResponse.json();

  return { props: { initialLogs: formattedLogs, initialStats: statsData } };
};

export default function Home({ initialLogs, initialStats }) {
  const [logs, setLogs] = useState(initialLogs);
  const [stats, setStats] = useState(initialStats);
  const [dataSource, setDataSource] = useState("live");
  const [lastUpdate, setLastUpdate] = useState("");

  useEffect(() => {
    if (dataSource === "live") {
      const fetchData = async () => {
        try {
          const [logsResponse, statsResponse] = await Promise.all([
            fetch("https://backend.anomala.cc/attack-logs"),
            fetch("https://backend.anomala.cc/stats")
          ]);

          const logsData = await logsResponse.json();
          const statsData = await statsResponse.json();

          setLogs(formatLogs(logsData.logs));
          setStats(statsData);
          setLastUpdate(logsData.timestamp);
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      };

      fetchData();
      const interval = setInterval(fetchData, 2000);
      return () => clearInterval(interval);
    }
  }, [dataSource]);

  const fetchSampleLogs = async () => {
    try {
      const response = await fetch('/api/logs');
      const data = await response.json();
      const formattedLogs = formatLogs(data.logs);
      setLogs(formattedLogs);
    } catch (error) {
      console.error('Error fetching sample logs:', error);
    }
  };

  const fetchSampleStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching sample stats:', error);
    }
  };

  const toggleDataSource = () => {
    const newSource = dataSource === "live" ? "sample" : "live";
    setDataSource(newSource);

    if (newSource === "sample") {
      fetchSampleLogs();
      fetchSampleStats();
    } else {
      setLogs(initialLogs);
      setStats(initialStats);
    }
  };

  return (
    <div className="min-h-screen bg-[#000000] text-white">
      <Navbar />
      <div className="container mx-auto p-6 space-y-6">
        <TitleHeader />
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleDataSource}
            className="px-4 py-2 rounded-lg bg-[#00ff94] text-black font-medium hover:bg-[#00ff94]/90 transition-colors"
          >
            {dataSource === "live" ? "Switch to Sample Data" : "Switch to Live Data"}
          </button>
        </div>
        <div className="space-y-6">
          <div className="w-full">
            <StatsCard stats={stats} />
          </div>
          <div className="w-full">
            <AttackChart logs={logs} />
          </div>
        </div>
        <LogsTable logs={logs} lastUpdate={lastUpdate} />
      </div>
    </div>
  );
}
