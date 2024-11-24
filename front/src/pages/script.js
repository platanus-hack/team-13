import { useEffect } from 'react';

export default function Script() {
    useEffect(() => {
        window.location.href = 'https://raw.githubusercontent.com/pv-hax/anomaly/refs/heads/main/anomaly.js';
    }, []);

    return null;
}
