import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Layers, AudioLinesIcon, UserCircle } from 'lucide-react';
import Profile from './Profile';
import PointAdjustment from './PointAdjustment';
import LevelAdjustment from './LevelAdjustment';

export default function Settings() {
  return (
    <div className="min-h-[calc(100vh-105px)] m-0 md:m-6 bg-white md:rounded-2xl">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-0 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="pt-2 h-auto border-b border-gray-200 bg-white mx-auto md:mx-0 w-[90%] lg:w-full rounded-none justify-start">
            <TabsTrigger
              value="profile"
              className="data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md md:px-4 py-2.5 data-[state=active]:shadow-none"
            >
              <UserCircle className="mr-2 size-6" />
              <span className="hidden sm:inline">Profile</span>
              <span className="sm:hidden">Profile</span>
            </TabsTrigger>
            <TabsTrigger
              value="point-adjustment"
              className="data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none ml-2"
            >
              <Layers className="mr-2 size-6" />
              <span className="hidden sm:inline">Points Adjustment</span>
              <span className="sm:hidden">Point</span>
            </TabsTrigger>
            <TabsTrigger
              value="level-adjustment"
              className="data-[state=active]:border-b-2 data-[state=active]:border-b-blue-600 data-[state=active]:text-blue-600 rounded-none rounded-t-md px-4 py-2.5 data-[state=active]:shadow-none ml-2"
            >
              <AudioLinesIcon className="mr-2 size-6" />
              <span className="hidden sm:inline">Levels Adjustment</span>
              <span className="sm:hidden">Level</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="mt-0">
            <Profile />
          </TabsContent>

          <TabsContent value="point-adjustment" className="mt-0">
            <PointAdjustment />
          </TabsContent>

          <TabsContent value="level-adjustment" className="mt-0">
            <LevelAdjustment />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}