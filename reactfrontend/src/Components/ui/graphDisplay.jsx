import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from './card';
import { CardContent } from './card';
import { CardHeader } from './card';
import { CardTitle } from './card';


const GraphDisplay = () => {
  const [monthlyTimeline, setMonthlyTimeline] = useState(null);
  const [weeklyActivity, setWeeklyActivity] = useState(null);
  const [dailyTimeline, setDailyTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGraphs = async () => {
      try {
        const monthlyResponse = await axios.get('http://127.0.0.1:8000/api/monthly-timeline');
        setMonthlyTimeline(monthlyResponse.data.monthly_timeline);

        const weeklyResponse = await axios.get('http://127.0.0.1:8000/api/weekly-activity-map');
        setWeeklyActivity(weeklyResponse.data.weekly_activity_map);

        const dailyResponse = await axios.get('http://127.0.0.1:8000/api/daily-timeline');
        setDailyTimeline(dailyResponse.data.daily_timeline);

        setLoading(false);
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setError('An error occurred while fetching graphs.');
        setLoading(false);
      }
    };

    fetchGraphs();
  }, []);

  if (loading) {
    return <p>Loading graphs...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div className="space-y-8">
      {monthlyTimeline && (
        <Card>
          <CardHeader>
            <CardTitle>Monthly Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={`data:image/png;base64,${monthlyTimeline}`}
              alt="Monthly Timeline"
              className="w-full rounded-lg shadow-md"
            />
          </CardContent>
        </Card>
      )}
      {weeklyActivity && (
        <Card>
          <CardHeader>
            <CardTitle>Weekly Activity Map</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={`data:image/png;base64,${weeklyActivity}`}
              alt="Weekly Activity Map"
              className="w-full rounded-lg shadow-md"
            />
          </CardContent>
        </Card>
      )}
      {dailyTimeline && (
        <Card>
          <CardHeader>
            <CardTitle>Daily Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={`data:image/png;base64,${dailyTimeline}`}
              alt="Daily Timeline"
              className="w-full rounded-lg shadow-md"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default GraphDisplay;
