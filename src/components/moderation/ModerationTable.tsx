"use client"
import React, { useEffect, useMemo, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { MoreVertical, AlertTriangle, VolumeX, Ban, CheckCircle } from 'lucide-react';
import { moderationData } from '@/data/Moderation';

const ModerationTable = () => {
  const [userType, setUserType] = useState<string>('All');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 7;

  // Get initials from name
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  };

  // Filter data by user type
  const filteredData = useMemo(() => {
    if (userType === 'All') return moderationData;
    return moderationData.filter(record => record.role === userType);
  }, [userType]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [userType]);

  const getActionBadge = (action: string) => {
    const baseClasses = 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border-2 border-dashed';
    
    switch (action) {
      case 'Warned':
        return (
          <span className={`${baseClasses} bg-yellow-50 text-yellow-700 border-yellow-300`}>
            <AlertTriangle className="w-3 h-3" />
            Warned
          </span>
        );
      case 'Muted':
        return (
          <span className={`${baseClasses} bg-gray-50 text-gray-700 border-gray-300`}>
            <VolumeX className="w-3 h-3" />
            Muted
          </span>
        );
      case 'Banned':
        return (
          <span className={`${baseClasses} bg-red-50 text-red-700 border-red-300`}>
            <Ban className="w-3 h-3" />
            Banned
          </span>
        );
      case 'UnBanned':
        return (
          <span className={`${baseClasses} bg-green-50 text-green-700 border-green-300`}>
            <CheckCircle className="w-3 h-3" />
            UnBanned
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="w-full rounded-lg p-4 md:p-6">
      {/* Header with filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 className="text-lg md:text-xl font-semibold text-gray-900">
          Moderation History ({filteredData.length})
        </h2>
        <div className="flex flex-col sm:flex-row gap-3">
          <Select value={userType} onValueChange={setUserType}>
            <SelectTrigger className="w-full sm:w-[140px]">
              <SelectValue placeholder="Select user type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              <SelectItem value="Student">Student</SelectItem>
              <SelectItem value="Teacher">Teacher</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Table - Desktop view */}
      <div className="hidden md:block overflow-x-auto bg-white rounded-lg p-2">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">No</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Action Taken</TableHead>
              <TableHead className="text-center">Warning</TableHead>
              <TableHead className="text-right w-[80px]">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.map((record) => (
              <TableRow key={record.id}>
                <TableCell className="font-medium">{record.id}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-blue-100 text-blue-700">
                        {getInitials(record.name)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-medium text-gray-900">{record.name}</div>
                      <div className="text-sm text-gray-500">{record.role}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-gray-600">{record.date}</TableCell>
                <TableCell>{getActionBadge(record.actionTaken)}</TableCell>
                <TableCell className="text-center font-medium">{record.warnings}</TableCell>
                <TableCell className="text-right">
                  <button className="inline-flex items-center justify-center w-8 h-8 rounded hover:bg-gray-100 transition-colors">
                    <MoreVertical className="w-4 h-4 text-gray-600" />
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-4">
        {paginatedData.map((record) => (
          <div key={record.id} className="border rounded-lg p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-blue-100 text-blue-700">
                    {getInitials(record.name)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium text-gray-900">{record.name}</div>
                  <div className="text-sm text-gray-500">{record.role}</div>
                </div>
              </div>
              <button className="inline-flex items-center justify-center w-8 h-8 rounded hover:bg-gray-100 transition-colors">
                <MoreVertical className="w-4 h-4 text-gray-600" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-500">Date:</span>
                <span className="ml-2 text-gray-900">{record.date}</span>
              </div>
              <div>
                <span className="text-gray-500">Warnings:</span>
                <span className="ml-2 font-medium text-gray-900">{record.warnings}</span>
              </div>
            </div>
            <div>{getActionBadge(record.actionTaken)}</div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex justify-end">
          <Pagination className='flex justify-end'>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setCurrentPage(Math.max(1, currentPage - 1));
                  }}
                  className={currentPage === 1 ? 'pointer-events-none opacity-50' : ''}
                />
              </PaginationItem>
              {[...Array(totalPages)].map((_, i) => (
                <PaginationItem key={i + 1}>
                  <PaginationLink 
                    href="#" 
                    isActive={currentPage === i + 1}
                    onClick={(e) => {
                      e.preventDefault();
                      setCurrentPage(i + 1);
                    }}
                  >
                    {i + 1}
                  </PaginationLink>
                </PaginationItem>
              ))}
              <PaginationItem>
                <PaginationNext 
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    setCurrentPage(Math.min(totalPages, currentPage + 1));
                  }}
                  className={currentPage === totalPages ? 'pointer-events-none opacity-50' : ''}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default ModerationTable;