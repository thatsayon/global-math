import { Menu } from "lucide-react";
import { Button } from "../ui/button";

const MobileMenuButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="lg:hidden"
      onClick={onClick}
    >
      <Menu className="h-6 w-6" />
    </Button>
  );
};

export default MobileMenuButton;