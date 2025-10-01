"use client"

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Plus, Pencil } from 'lucide-react';
import { toast } from 'sonner';

// Level form schema
const levelSchema = z.object({
  level: z.string().min(1, 'Level is required'),
  name: z.string().min(1, 'Name is required'),
  point: z.string().min(1, 'Point is required'),
});

type LevelFormData = z.infer<typeof levelSchema>;

interface Level {
  id: string;
  level: string;
  name: string;
  point: string;
}

export default function LevelAdjustment() {
  const [levels, setLevels] = useState<Level[]>([
    { id: '1', level: '01', name: 'Algebra', point: '10' },
    { id: '2', level: '02', name: 'Geometry', point: '20' },
    { id: '3', level: '03', name: 'Pre-Calculus', point: '30' },
    { id: '4', level: '04', name: 'Statistics', point: '40' },
  ]);

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingLevel, setEditingLevel] = useState<Level | null>(null);

  // Add form
  const addForm = useForm<LevelFormData>({
    resolver: zodResolver(levelSchema),
    defaultValues: {
      level: '',
      name: '',
      point: '',
    },
  });

  // Edit form
  const editForm = useForm<LevelFormData>({
    resolver: zodResolver(levelSchema),
    defaultValues: {
      level: '',
      name: '',
      point: '',
    },
  });

  const onAddLevel = (data: LevelFormData) => {
    console.log('Adding Level:', data);
    
    const newLevel: Level = {
      id: Date.now().toString(),
      level: data.level.padStart(2, '0'),
      name: data.name,
      point: data.point,
    };

    setLevels([...levels, newLevel]);
    addForm.reset();

    toast.success("Level Added",{
      description: "New level has been added successfully.",
    });
  };

  const handleEditClick = (level: Level) => {
    setEditingLevel(level);
    editForm.reset({
      level: level.level,
      name: level.name,
      point: level.point,
    });
    setIsEditDialogOpen(true);
  };

  const onEditLevel = (data: LevelFormData) => {
    if (!editingLevel) return;

    console.log('Editing Level:', data);

    setLevels(levels.map(level => 
      level.id === editingLevel.id 
        ? { ...level, level: data.level.padStart(2, '0'), name: data.name, point: data.point }
        : level
    ));

    setIsEditDialogOpen(false);
    setEditingLevel(null);

    toast.success("Level Updated",{
      description: "Level has been updated successfully.",
    });
  };

  const onSave = () => {
    console.log('Saving all levels:', levels);
    toast.success("Changes Saved",{
      description: "All level adjustments have been saved.",
    });
  };

  const onCancel = () => {
    addForm.reset();
    toast.info("Changes Discarded",{
      description: "All changes have been cancelled.",
    });
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg border p-6 space-y-6">
        <h2 className="text-2xl font-semibold">Level</h2>

        {/* Add Level Form */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="level">Level</Label>
            <div className="relative">
              <Input
                id="level"
                placeholder="---"
                {...addForm.register('level')}
                className="w-full pr-10"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {addForm.formState.errors.level && (
              <p className="text-sm text-red-500">
                {addForm.formState.errors.level.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <div className="relative">
              <Input
                id="number"
                placeholder="---"
                {...addForm.register('name')}
                className="w-full pr-10"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {addForm.formState.errors.name && (
              <p className="text-sm text-red-500">
                {addForm.formState.errors.name.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="point">Point</Label>
            <div className="relative">
              <Input
                id="point"
                type="number"
                placeholder="---"
                {...addForm.register('point')}
                className="w-full pr-10"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {addForm.formState.errors.point && (
              <p className="text-sm text-red-500">
                {addForm.formState.errors.point.message}
              </p>
            )}
          </div>
        </div>

        {/* Add Button */}
        <div className="flex justify-end">
          <Button
            onClick={addForm.handleSubmit(onAddLevel)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add
          </Button>
        </div>

        {/* Levels Table */}
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-center">Level</TableHead>
                <TableHead className="text-center">Name</TableHead>
                <TableHead className="text-center">Point</TableHead>
                <TableHead className="text-center">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {levels.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-gray-500 py-8">
                    No levels added yet. Add your first level above.
                  </TableCell>
                </TableRow>
              ) : (
                levels.map((level) => (
                  <TableRow key={level.id}>
                    <TableCell className="text-center">{level.level}</TableCell>
                    <TableCell className="text-center">{level.name}</TableCell>
                    <TableCell className="text-center">{level.point}</TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditClick(level)}
                        className="flex items-center gap-2 mx-auto"
                      >
                        <Pencil className="h-3 w-3" />
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
          <Button 
            onClick={onSave}
            className="w-full sm:w-auto px-8"
          >
            Save
          </Button>
          <Button 
            onClick={onCancel}
            variant="outline"
            className="w-full sm:w-auto px-8 border-red-500 text-red-500 hover:bg-red-50"
          >
            Cancel
          </Button>
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Level</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-level">Level</Label>
              <Input
                id="edit-level"
                placeholder="---"
                {...editForm.register('level')}
              />
              {editForm.formState.errors.level && (
                <p className="text-sm text-red-500">
                  {editForm.formState.errors.level.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-number">Number</Label>
              <Input
                id="edit-number"
                placeholder="---"
                {...editForm.register('name')}
              />
              {editForm.formState.errors.name && (
                <p className="text-sm text-red-500">
                  {editForm.formState.errors.name.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-point">Point</Label>
              <Input
                id="edit-point"
                type="number"
                placeholder="---"
                {...editForm.register('point')}
              />
              {editForm.formState.errors.point && (
                <p className="text-sm text-red-500">
                  {editForm.formState.errors.point.message}
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="flex items-center gap-3 ">
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={editForm.handleSubmit(onEditLevel)}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}