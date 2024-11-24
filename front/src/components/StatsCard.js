export default function StatsCard({ stats }) {
    // Only consider the attack types we're showing
    const relevantAttackTypes = {
        sql_injection: stats.types_of_attacks.sql_injection || 0,
        xss: stats.types_of_attacks.xss || 0,
        phishing: stats.types_of_attacks.phishing || 0,
        unknown: stats.types_of_attacks.unknown || 0
    };

    // Calculate total frequency from relevant attack types
    const totalFrequency = Object.values(relevantAttackTypes).reduce((sum, freq) => sum + freq, 0);

    // Calculate percentages for each attack type
    const attackPercentages = {
        sql_injection: Math.round((relevantAttackTypes.sql_injection / totalFrequency) * 100),
        xss: Math.round((relevantAttackTypes.xss / totalFrequency) * 100),
        phishing: Math.round((relevantAttackTypes.phishing / totalFrequency) * 100),
        unknown: Math.round((relevantAttackTypes.unknown / totalFrequency) * 100)
    };

    return (
        <div className="w-full p-6 rounded-xl relative overflow-hidden border border-white/10 backdrop-blur-md bg-[#121212]/80">
            <div className="relative z-10">
                <div className="grid grid-cols-2 gap-6 mb-8">
                    <div>
                        <h3 className="text-sm text-gray-400 mb-2">Total Attacks</h3>
                        <p className="font-inter font-light text-3xl text-white">{stats.total_attacks}</p>
                    </div>

                    <div>
                        <h3 className="text-sm text-gray-400 mb-2">Blocked Attacks</h3>
                        <p className="font-inter font-light text-3xl text-white">{stats.total_blocked}</p>
                    </div>
                </div>

                <div>
                    <h3 className="text-sm text-gray-400 mb-4">Attack Types Distribution</h3>
                    <div className="flex h-4 rounded-full overflow-hidden bg-white/5">
                        <div
                            className="bg-[#00ff94]/80 transition-all duration-500"
                            style={{ width: `${attackPercentages.sql_injection}%` }}
                        />
                        <div
                            className="bg-[#00ff94]/50 transition-all duration-500"
                            style={{ width: `${attackPercentages.xss}%` }}
                        />
                        <div
                            className="bg-[#00ff94]/20 transition-all duration-500"
                            style={{ width: `${attackPercentages.phishing}%` }}
                        />
                        <div
                            className="bg-[#00ff94]/10 transition-all duration-500"
                            style={{ width: `${attackPercentages.unknown}%` }}
                        />
                    </div>
                    <div className="flex justify-between mt-2 text-xs">
                        <div className="flex items-center">
                            <div className="w-2 h-2 rounded-full bg-[#00ff94]/80 mr-2" />
                            <span className="text-gray-400">SQL ({attackPercentages.sql_injection}%)</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-2 h-2 rounded-full bg-[#00ff94]/50 mr-2" />
                            <span className="text-gray-400">XSS ({attackPercentages.xss}%)</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-2 h-2 rounded-full bg-[#00ff94]/20 mr-2" />
                            <span className="text-gray-400">Phishing ({attackPercentages.phishing}%)</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-2 h-2 rounded-full bg-[#00ff94]/10 mr-2" />
                            <span className="text-gray-400">Unknown ({attackPercentages.unknown}%)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
} 