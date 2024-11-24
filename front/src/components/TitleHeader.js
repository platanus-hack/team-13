export default function TitleHeader() {
    return (
        <div className="text-center py-6 relative">
            {/* Main background glow - positioned directly behind title */}
            <div className="absolute inset-0 flex justify-center items-center">
                <div className="w-[600px] h-[400px] bg-[#00ff94] rounded-full filter blur-[120px] opacity-[0.04] animate-pulse"></div>
            </div>

            {/* Secondary glow behind title */}
            <div className="absolute inset-0 flex justify-center items-center">
                <div className="w-64 h-64 bg-[#00ff94] rounded-full filter blur-[100px] opacity-10 animate-pulse"></div>
            </div>

            {/* 3D Title */}
            <div className="relative z-10">
                <h1 className={`
                    uppercase
                    text-5xl
                    font-bold
                    tracking-widest
                    text-transparent
                    bg-clip-text
                    bg-gradient-to-r
                    from-[#00ff94]
                    via-[#80ffca]
                    to-[#00ff94]
                    [text-shadow:_
                        0_0_10px_rgba(0,255,148,0.8),
                        0_0_20px_rgba(0,255,148,0.4),
                        0_0_30px_rgba(0,255,148,0.2),
                        1px_1px_2px_rgba(0,255,148,0.8)
                    ]
                    font-['Oxanium']
                    transition-all
                    duration-300
                    hover:scale-105
                `}>
                    ANOMALA
                </h1>
            </div>

            {/* Decorative elements */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/4 w-1 h-1 bg-[#00ff94] rounded-full animate-ping"></div>
                <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-[#00ff94] rounded-full animate-ping delay-100"></div>
                <div className="absolute bottom-1/2 right-1/4 w-1 h-1 bg-[#00ff94] rounded-full animate-ping delay-200"></div>
            </div>

            {/* Font import */}
            <link
                href="https://fonts.googleapis.com/css2?family=Oxanium:wght@700&display=swap"
                rel="stylesheet"
            />

            {/* Minimal styles for glow effect */}
            <style jsx global>{`
                @keyframes glow {
                    0%, 100% {
                        text-shadow: 
                            0 0 10px rgba(0,255,148,0.8),
                            0 0 20px rgba(0,255,148,0.4),
                            0 0 30px rgba(0,255,148,0.2);
                    }
                    50% {
                        text-shadow: 
                            0 0 15px rgba(0,255,148,0.8),
                            0 0 25px rgba(0,255,148,0.4),
                            0 0 35px rgba(0,255,148,0.2);
                    }
                }
            `}</style>
        </div>
    );
} 