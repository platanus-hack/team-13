import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useState } from 'react';

export default function AttackChart({ logs }) {
    const [timeframe, setTimeframe] = useState('daily');

    const getHistogramData = () => {
        if (timeframe === 'daily') {
            // Daily data calculation
            const hourlyBins = logs.reduce((acc, log) => {
                const hour = new Date(log.timestamp).getHours();
                acc[hour] = (acc[hour] || 0) + 1;
                return acc;
            }, {});

            return Array.from({ length: 24 }, (_, hour) => ({
                hour: hour,
                frequency: hourlyBins[hour] || 0,
                label: hour.toString().padStart(2, '0')
            }));
        } else {
            // Weekly data calculation
            const weeklyBins = logs.reduce((acc, log) => {
                const day = new Date(log.timestamp).getDay();
                acc[day] = (acc[day] || 0) + 1;
                return acc;
            }, {});

            return Array.from({ length: 7 }, (_, day) => ({
                day: day,
                frequency: weeklyBins[day] || 0,
                label: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][day]
            }));
        }
    };

    return (
        <div className="w-full p-6 rounded-xl relative overflow-hidden border border-white/10 bg-[#090909]">
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-tl from-[#00ff94] via-[#00ff9415] to-transparent opacity-15" />
                <div className="absolute inset-0 bg-gradient-to-tl from-[#00ff94] via-transparent to-transparent opacity-10" />
            </div>
            <div className="relative z-10">
                <div className="mb-6">
                    <div className="mb-2">
                        <h2 className="font-inter font-light text-2xl text-white mb-2">Detected attacks</h2>
                        <p className="text-sm text-gray-400 mb-8">Grouped by units of time</p>
                    </div>
                    <div className="flex gap-6 text-sm">
                        <button
                            onClick={() => setTimeframe('daily')}
                            className={`text-base font-medium ${timeframe === 'daily' ? 'text-[#00ff94]' : 'text-white'
                                }`}
                        >
                            Daily
                        </button>
                        <button
                            onClick={() => setTimeframe('weekly')}
                            className={`text-base font-medium ${timeframe === 'weekly' ? 'text-[#00ff94]' : 'text-white'
                                }`}
                        >
                            Weekly
                        </button>
                    </div>
                </div>
                <div className="h-[300px] mb-12">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={getHistogramData()}
                            margin={{ top: 20, right: 30, left: 20, bottom: 30 }}
                        >
                            <defs>
                                <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#00ff94" stopOpacity={1} />
                                    <stop offset="100%" stopColor="#00ff94" stopOpacity={0.6} />
                                </linearGradient>
                                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#00ff94" stopOpacity={0.1} />
                                    <stop offset="50%" stopColor="#00ff94" stopOpacity={0.2} />
                                    <stop offset="100%" stopColor="#00ff94" stopOpacity={0.4} />
                                </linearGradient>
                                <radialGradient id="glowGradient" cx="50%" cy="50%" r="70%">
                                    <stop offset="0%" stopColor="#00ff94" stopOpacity={0.3} />
                                    <stop offset="100%" stopColor="#00ff94" stopOpacity={0} />
                                </radialGradient>
                            </defs>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="rgba(255,255,255,0.1)"
                                vertical={false}
                            />
                            <XAxis
                                dataKey="label"
                                stroke="#ffffff"
                                tick={{
                                    fill: 'rgba(255, 255, 255, 0.4)',
                                    dy: 10
                                }}
                                axisLine={{ stroke: '#ffffff40' }}
                                dy={10}
                                tickMargin={20}
                            />
                            <YAxis
                                stroke="#ffffff"
                                tick={{
                                    fill: 'rgba(255, 255, 255, 0.4)',
                                    dx: -10
                                }}
                                axisLine={{ stroke: '#ffffff40' }}
                                tickMargin={5}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                    border: '1px solid rgba(255, 255, 255, 0.2)',
                                    borderRadius: '8px',
                                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                                }}
                                labelStyle={{ color: '#ffffff' }}
                                itemStyle={{ color: '#ffffff' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="frequency"
                                stroke="url(#lineGradient)"
                                strokeWidth={3}
                                fill="url(#areaGradient)"
                                dot={{
                                    fill: '#000000',
                                    stroke: '#00ff94',
                                    strokeWidth: 2,
                                    r: 4
                                }}
                                activeDot={{
                                    fill: '#00ff94',
                                    stroke: '#000000',
                                    strokeWidth: 2,
                                    r: 6
                                }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
} 