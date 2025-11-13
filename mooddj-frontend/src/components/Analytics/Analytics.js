import React from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data - this will come from your backend later
const mockMoodData = [
  { time: '10:00', happy: 0.8, sad: 0.1, neutral: 0.1 },
  { time: '10:05', happy: 0.7, sad: 0.2, neutral: 0.1 },
  { time: '10:10', happy: 0.6, sad: 0.3, neutral: 0.1 },
  { time: '10:15', happy: 0.4, sad: 0.4, neutral: 0.2 },
  { time: '10:20', happy: 0.5, sad: 0.3, neutral: 0.2 },
];

const stats = [
  { label: 'Songs Played', value: '0' },
  { label: 'Mood Changes', value: '0' },
  { label: 'Session Time', value: '0:00' },
  { label: 'Dominant Mood', value: 'Neutral' },
];

function Analytics() {
  return (
    <Box>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {stats.map((stat, index) => (
          <Grid item xs={6} md={3} key={index}>
            <Card sx={{ bgcolor: 'background.default' }}>
              <CardContent>
                <Typography variant="h4" color="primary.main">
                  {stat.value}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="subtitle2" gutterBottom>
        Mood Timeline
      </Typography>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={mockMoodData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" stroke="#999" />
          <YAxis stroke="#999" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1E1E1E',
              border: '1px solid #333',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="happy"
            stroke="#4CAF50"
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="sad"
            stroke="#2196F3"
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="neutral"
            stroke="#9E9E9E"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}

export default Analytics;
