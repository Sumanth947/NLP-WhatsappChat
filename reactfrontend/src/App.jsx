import React, { useState } from 'react';
import axios from 'axios';
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../src/Components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import { Loader2 } from "lucide-react";
import GraphDisplay from './Components/ui/graphDisplay';  // Import the new component
import ChatBot from './Components/ui/chatbot';

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data);
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while analyzing the chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 dark:from-gray-900 dark:to-gray-800 overflow-hidden">
      <div className="container mx-auto p-4">
        <h1 className="text-4xl font-bold mb-8 text-center text-purple-800 dark:text-purple-300">
          WhatsApp Chat Analyzer
        </h1>
        <Card className="mb-8 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center space-x-2">
                <Input type="file" onChange={handleFileChange} accept=".txt,.csv" />
                <Button type="submit" disabled={!file || loading} className="bg-purple-600 hover:bg-purple-700 text-white">
                  {loading ? <Loader2 className="animate-spin mr-2 h-5 w-5" /> : 'Analyze Chat'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive" className="mb-6 bg-red-100 border-red-400 text-red-700">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {results && (
          <>
            {/* Top Statistics */}
            <div className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Total Messages</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-semibold">{results.total_messages}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Total Words</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-semibold">{results.words}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Media Shared</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-semibold">{results.num_media}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Links Shared</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-semibold">{results.num_links}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Display the Graphs */}
              <GraphDisplay />

              {/* Add ChatBot */}
              <div className="mt-8">
                <ChatBot />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
