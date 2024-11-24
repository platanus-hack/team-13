import path from 'path';
import { promises as fs } from 'fs';

export default async function handler(req, res) {
    try {
        // Get the path to the JSON file
        const jsonDirectory = path.join(process.cwd(), 'src/data');
        // Read the JSON file
        const fileContents = await fs.readFile(jsonDirectory + '/sample_stats.json', 'utf8');
        // Parse and return the data
        const data = JSON.parse(fileContents);
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ error: 'Failed to load data' });
    }
} 