import Navbar from '../components/Navbar';

const Replay = () => {
    return (
        <div className="min-h-screen bg-[#000000] text-white">
            <Navbar />
            <div className="h-screen w-screen relative bg-white">
                <iframe
                    className="rounded-xl absolute h-full w-full mx-auto"
                    src="https://pub-35718f4f99a643cb9417ba5cd82c0dbc.r2.dev/test-replay/replay.html"
                />
            </div>
        </div>
    );
}

export default Replay;