import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

export interface NavSubItem {
  label: string;
  description: string;
  icon: React.ElementType;
  onClick?: () => void;
  badge?: string;
}

export interface NavSubGroup {
  title: string;
  items: NavSubItem[];
}

export interface NavItem {
  id: string | number;
  label: string;
  subMenus?: NavSubGroup[];
  onClick?: () => void;
}

interface DropdownNavigationProps {
  navItems: NavItem[];
  activeId?: string | number;
}

export function DropdownNavigation({ navItems, activeId }: DropdownNavigationProps) {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [isHover, setIsHover] = useState<string | number | null>(null);

  const handleHover = (menuLabel: string | null) => {
    setOpenMenu(menuLabel);
  };

  return (
    <ul className="relative flex items-center space-x-1">
      {navItems.map((navItem) => {
        const isActive = activeId === navItem.id;
        const isOpen = openMenu === navItem.label;

        return (
          <li
            key={navItem.label}
            className="relative"
            onMouseEnter={() => handleHover(navItem.label)}
            onMouseLeave={() => handleHover(null)}
          >
            <button
              onClick={() => navItem.onClick?.()}
              className={`text-xs font-medium py-1.5 px-3 flex cursor-pointer group transition-colors duration-200 items-center justify-center gap-1 relative rounded-md ${
                isActive
                  ? 'text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              onMouseEnter={() => setIsHover(navItem.id)}
              onMouseLeave={() => setIsHover(null)}
            >
              <span>{navItem.label}</span>
              {navItem.subMenus && (
                <ChevronDown
                  className={`h-3 w-3 transition-transform duration-200 opacity-60 group-hover:opacity-100 ${
                    isOpen ? 'rotate-180 text-primary' : ''
                  }`}
                />
              )}

              {/* Hover Pill Background */}
              {isHover === navItem.id && (
                <motion.div
                  layoutId="nav-hover-bg"
                  className="absolute inset-0 size-full bg-muted -z-10 rounded-md"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}

              {/* Active Bottom Indicator Line */}
              {isActive && (
                <motion.div
                  layoutId="nav-active-line"
                  className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                  transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                />
              )}
            </button>

            {/* Dropdown Menu */}
            <AnimatePresence>
              {isOpen && navItem.subMenus && (
                <div className="w-auto absolute left-0 top-full pt-2 z-50">
                  <motion.div
                    initial={{ opacity: 0, y: 6, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 4, scale: 0.98 }}
                    transition={{ duration: 0.15, ease: 'easeOut' }}
                    className="bg-card border border-border p-4 rounded-xl shadow-xl w-max min-w-[280px]"
                  >
                    <div className="w-fit shrink-0 flex gap-8 overflow-hidden">
                      {navItem.subMenus.map((sub) => (
                        <div className="w-full" key={sub.title}>
                          <h3 className="mb-3 text-[11px] font-mono font-medium uppercase tracking-wider text-muted-foreground">
                            {sub.title}
                          </h3>
                          <ul className="space-y-2.5">
                            {sub.items.map((item) => {
                              const Icon = item.icon;
                              return (
                                <li key={item.label}>
                                  <button
                                    onClick={() => {
                                      item.onClick?.();
                                      setOpenMenu(null);
                                    }}
                                    className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted/80 text-left w-full group/item transition-colors cursor-pointer"
                                  >
                                    <div className="border border-border bg-card text-foreground rounded-lg flex items-center justify-center size-8 shrink-0 group-hover/item:border-primary group-hover/item:text-primary transition-colors">
                                      <Icon className="h-4 w-4" />
                                    </div>
                                    <div className="leading-tight">
                                      <div className="flex items-center gap-1.5">
                                        <p className="text-xs font-semibold text-foreground group-hover/item:text-primary transition-colors">
                                          {item.label}
                                        </p>
                                        {item.badge && (
                                          <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-muted text-primary border border-border">
                                            {item.badge}
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-1 max-w-[220px]">
                                        {item.description}
                                      </p>
                                    </div>
                                  </button>
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              )}
            </AnimatePresence>
          </li>
        );
      })}
    </ul>
  );
}

export default DropdownNavigation;
