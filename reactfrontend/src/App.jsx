import React, { useState, useEffect } from 'react';
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import { Loader2, Upload, BarChart, PieChart, MessageSquare } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowWelcome(false), 3000);
    return () => clearTimeout(timer);
  }, []);

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
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Failed to analyze chat');
      }
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while analyzing the chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 dark:from-gray-900 dark:to-gray-800 overflow-hidden">
      <AnimatePresence>
        {showWelcome && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
          >
            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <h2 className="text-3xl font-bold text-purple-600 mb-4">Welcome to WhatsApp Chat Analyzer</h2>
              <p className="text-gray-600">Upload your chat and get insights in seconds!</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="container mx-auto p-4">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-4xl font-bold mb-8 text-center text-purple-800 dark:text-purple-300"
        >
          WhatsApp Chat Analyzer
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card className="mb-8 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="flex items-center space-x-2">
                  <div className="relative flex-grow">
                    <Input 
                      type="file" 
                      onChange={handleFileChange} 
                      className="hidden" 
                      id="file-upload"
                      accept=".txt,.csv" 
                    />
                    <label 
                      htmlFor="file-upload" 
                      className="flex items-center justify-center w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 cursor-pointer transition-colors duration-300"
                    >
                      <Upload className="w-5 h-5 mr-2" />
                      {file ? file.name : 'Choose file'}
                    </label>
                  </div>
                  <Button 
                    type="submit" 
                    disabled={!file || loading}
                    className="bg-purple-600 hover:bg-purple-700 text-white transition-colors duration-300"
                  >
                    {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : null}
                    {loading ? 'Analyzing...' : 'Analyze Chat'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Alert variant="destructive" className="mb-6 bg-red-100 border-red-400 text-red-700">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {results && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm transform transition-all hover:scale-105">
                  <CardHeader className="bg-purple-100 dark:bg-purple-900">
                    <CardTitle className="flex items-center text-purple-800 dark:text-purple-200">
                      <MessageSquare className="w-6 h-6 mr-2" />
                      Total Messages
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.p 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 260, damping: 20 }}
                      className="text-5xl font-bold text-center py-4 text-purple-600 dark:text-purple-400"
                    >
                      {results.total_messages}
                    </motion.p>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm transform transition-all hover:scale-105">
                  <CardHeader className="bg-indigo-100 dark:bg-indigo-900">
                    <CardTitle className="flex items-center text-indigo-800 dark:text-indigo-200">
                      <BarChart className="w-6 h-6 mr-2" />
                      Topic Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.img 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                      src={`data:image/png;base64,${results.topic_plot}`} 
                      alt="Topic Distribution" 
                      className="w-full rounded-lg shadow-md" 
                    />
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm transform transition-all hover:scale-105">
                  <CardHeader className="bg-blue-100 dark:bg-blue-900">
                    <CardTitle className="flex items-center text-blue-800 dark:text-blue-200">
                      <PieChart className="w-6 h-6 mr-2" />
                      Sentiment Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.img 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.8 }}
                      src={`data:image/png;base64,${results.sentiment_plot}`} 
                      alt="Sentiment Distribution" 
                      className="w-full rounded-lg shadow-md" 
                    />
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
              >
                <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm transform transition-all hover:scale-105">
                  <CardHeader className="bg-green-100 dark:bg-green-900">
                    <CardTitle className="flex items-center text-green-800 dark:text-green-200">
                      <BarChart className="w-6 h-6 mr-2" />
                      Sentiment Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {Object.entries(results.sentiment_distribution).map(([sentiment, count], index) => (
                        <motion.li 
                          key={sentiment}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 1 + (index * 0.1) }}
                          className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-800 rounded-md"
                        >
                          <span className="font-semibold text-green-700 dark:text-green-200">{sentiment}</span>
                          <span className="bg-green-200 dark:bg-green-700 text-green-800 dark:text-green-100 px-2 py-1 rounded-full text-sm">{count}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}