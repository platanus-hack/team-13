import Link from 'next/link';

export default function Navbar() {
    return (
        <nav className="sticky top-0 z-50 backdrop-blur-md bg-black/30 border-b border-white/10">
            <div className="container mx-auto px-6 py-4">
                <div className="flex items-center justify-end space-x-12">
                    <Link
                        href="#"
                        className="text-white/80 hover:text-[#00ff94] transition-colors duration-200"
                    >
                        Contact Us
                    </Link>
                    <Link
                        href="#"
                        className="text-white/80 hover:text-[#00ff94] transition-colors duration-200"
                    >
                        About
                    </Link>
                    <div className="flex items-center space-x-3 ml-8">
                        <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
                            <img
                                src="https://i.pravatar.cc/105"
                                alt="Profile"
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <span className="text-white/80">John Anderson</span>
                    </div>
                </div>
            </div>
        </nav>
    );
} 