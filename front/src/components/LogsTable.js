import { useState, useEffect } from 'react';

const LoadingCircle = ({ isUpdated }) => (
    <div className="ml-2 inline-block w-4 h-4 relative">
        <div className={`
            absolute w-4 h-4 border-2 rounded-full animate-spin
            transition-colors duration-300
            ${isUpdated ? 'border-[#00ff94] border-t-transparent' : 'border-gray-400 border-t-transparent'}
        `} />
    </div>
);

export default function LogsTable({ logs, lastUpdate }) {
    const [sortConfig, setSortConfig] = useState({
        key: 'timestamp',
        direction: 'desc'
    });
    const [sortedLogs, setSortedLogs] = useState(logs);
    const [isUpdated, setIsUpdated] = useState(false);

    // Sort function
    const sortLogs = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }

        const sorted = [...logs].sort((a, b) => {
            if (key === 'timestamp') {
                return direction === 'asc'
                    ? new Date(a[key]) - new Date(b[key])
                    : new Date(b[key]) - new Date(a[key]);
            }

            if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
            if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        setSortedLogs(sorted);
        setSortConfig({ key, direction });
    };

    // Update sorted logs when props change
    useEffect(() => {
        setSortedLogs(logs);
    }, [logs]);

    useEffect(() => {
        setIsUpdated(true);
        const timer = setTimeout(() => setIsUpdated(false), 300);
        return () => clearTimeout(timer);
    }, [lastUpdate]);

    // Sort indicator component
    const SortIndicator = ({ columnKey }) => {
        if (sortConfig.key !== columnKey) return <span className="ml-1">↕</span>;
        return <span className="ml-1">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
    };

    const handleUnban = async (ip) => {
        try {
            const response = await fetch('https://backend.anomala.cc/unban-all', {
                method: 'POST',
            });
            if (!response.ok) throw new Error('Failed to unban IP');
            // You might want to add some success feedback here
        } catch (error) {
            console.error('Error unbanning IP:', error);
            // You might want to add some error feedback here
        }
    };

    return (
        <div className="overflow-hidden rounded-xl relative border border-white/10 bg-black">
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-bl from-white via-white/10 to-transparent opacity-[0.02]" />
                <div className="absolute inset-0 bg-gradient-to-bl from-white via-transparent to-transparent opacity-[0.03]" />
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white via-white/10 to-transparent opacity-[0.08]" />
            </div>
            <div className="relative z-10 p-6 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-inter font-light text-2xl text-white mb-2">Logs</h2>
                <div className="flex items-center">
                    <span className={`
                        text-sm transition-colors duration-300
                        ${isUpdated ? 'text-[#00ff94]' : 'text-gray-400'}
                    `}>
                        {new Date(lastUpdate).toLocaleTimeString()}
                    </span>
                    <LoadingCircle isUpdated={isUpdated} />
                </div>
            </div>
            <div className="relative z-10 overflow-x-auto">
                <table className="min-w-full divide-y divide-white/10">
                    <thead className="bg-black/40">
                        <tr>
                            <th
                                className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:text-white/80"
                                onClick={() => sortLogs('timestamp')}
                            >
                                Timestamp
                                <SortIndicator columnKey="timestamp" />
                            </th>
                            <th
                                className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:text-white/80"
                                onClick={() => sortLogs('ip')}
                            >
                                IP
                                <SortIndicator columnKey="ip" />
                            </th>
                            <th
                                className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:text-white/80"
                                onClick={() => sortLogs('type_of_attack')}
                            >
                                Type of Attack
                                <SortIndicator columnKey="type_of_attack" />
                            </th>
                            <th
                                className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:text-white/80"
                                onClick={() => sortLogs('blocked')}
                            >
                                Status
                                <SortIndicator columnKey="blocked" />
                            </th>
                            <th
                                className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:text-white/80"
                                onClick={() => sortLogs('confidence_score')}
                            >
                                Confidence
                                <SortIndicator columnKey="confidence_score" />
                            </th>
                            <th className="px-6 py-4 text-left text-xs font-medium text-white uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                        {sortedLogs.map((log, index) => (
                            <tr
                                key={index}
                                className="transition-colors duration-150 hover:bg-white/5"
                            >
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="text-gray-300">
                                        {log.formattedDate}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                                    <a
                                        href={`/replay`}
                                        className="text-gray-300 hover:text-[#00ff94] transition-colors duration-200"
                                    >
                                        {log.ip}
                                    </a>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="text-gray-300">
                                        {log.type_of_attack}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className={`
                                        px-3 py-1 rounded-full text-xs font-medium
                                        ${log.blocked
                                            ? 'bg-red-900/50 text-red-200 border border-red-700'
                                            : 'bg-[#00ff9415] text-[#00ff94] border border-[#00ff94]/20'
                                        }
                                    `}>
                                        {log.blocked ? 'Blocked' : 'Not Blocked'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <div className="flex items-center">
                                        <div className={`w-3 h-3 rounded-full mr-2 ${log.confidence_score >= 0.66
                                            ? 'bg-[#00ff94]'
                                            : log.confidence_score >= 0.33
                                                ? 'bg-yellow-400'
                                                : 'bg-red-500'
                                            }`} />
                                        <span className="text-gray-300">
                                            {Math.round(log.confidence_score * 100)}%
                                        </span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {log.blocked && (
                                        <button
                                            onClick={() => handleUnban(log.ip)}
                                            className="px-3 py-1 rounded-lg bg-red-900/30 text-red-200 border border-red-700/30 hover:bg-red-900/50 hover:border-red-700/50 transition-colors duration-200"
                                        >
                                            Unban
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
} 