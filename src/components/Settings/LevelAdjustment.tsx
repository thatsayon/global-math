// components/settings/LevelAdjustment.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Plus, Pencil } from "lucide-react";
import { toast } from "sonner";
import {
  useCreateMathLevelMutation,
  useGetMathLevelsQuery,
  useUpdateMathLevelMutation,
} from "@/store/slices/api/profileApiSlice";
import { useState } from "react";
import { LoadingState } from "../elements/Loading";

const levelSchema = z.object({
  name: z.string().min(1, "Name is required"),
});

type LevelFormData = z.infer<typeof levelSchema>;

export default function LevelAdjustment() {
  const { data: levelsData, isLoading } = useGetMathLevelsQuery();
  const [createLevel, { isLoading: creating }] = useCreateMathLevelMutation();
  const [updateLevel, { isLoading: updating }] = useUpdateMathLevelMutation();

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const addForm = useForm<LevelFormData>({
    resolver: zodResolver(levelSchema),
  });
  const editForm = useForm<LevelFormData>({
    resolver: zodResolver(levelSchema),
  });

  const levels = levelsData?.results || [];

  const onAddLevel = async (data: LevelFormData) => {
    try {
      await createLevel({ name: data.name }).unwrap();
      toast.success("Level Added");
      addForm.reset();
    } catch (error) {
      const err = error as { data: { name: string } };

      toast.error("Failed", {
        description: err.data?.name || "Already exists",
      });
    }
  };

  const openEdit = (level: (typeof levels)[0]) => {
    setEditingId(level.id);
    editForm.reset({ name: level.name });
    setIsEditDialogOpen(true);
  };

  const onEditLevel = async (data: LevelFormData) => {
    if (!editingId) return;
    try {
      await updateLevel({ id: editingId, data }).unwrap();
      toast.success("Level Updated");
      setIsEditDialogOpen(false);
    } catch (error) {
      const err = error as { data: { name: string } };
      toast.error("Failed", {
        description: err.data?.name || "Update failed",
      });
    }
  };

  if (isLoading)
    return (
      <div>
        <LoadingState />
      </div>
    );

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg border p-6 space-y-6">
        <h2 className="text-2xl font-semibold">Level Adjustment</h2>

        <div className="flex gap-4 items-end">
          <div className="flex-1 space-y-2">
            <Label>Name</Label>
            <Input
              {...addForm.register("name")}
              placeholder="Enter level name"
            />
          </div>
          <Button
            onClick={addForm.handleSubmit(onAddLevel)}
            disabled={creating}
          >
            <Plus className="h-4 w-4 mr-2" /> Add
          </Button>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {levels.map((level) => (
              <TableRow key={level.id}>
                <TableCell>{level.name}</TableCell>
                <TableCell className="font-mono text-sm">
                  {level.slug}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openEdit(level)}
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Level</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Name</Label>
              <Input {...editForm.register("name")} />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={editForm.handleSubmit(onEditLevel)}
              disabled={updating}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
