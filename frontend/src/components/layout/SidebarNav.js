import Image from "next/image";
import {
  FiBarChart2,
  FiBookOpen,
  FiClipboard,
  FiFileText,
  FiFolder,
  FiGrid,
  FiLayers,
  FiSettings,
} from "react-icons/fi";

export const defaultNavItems = [
  { icon: FiGrid, label: "Dashboard", route: "/dashboard" },
  { icon: FiFileText, label: "Create Content", route: "/create-content" },
  { icon: FiFolder, label: "My Jobs", route: "/my-jobs" },
  { icon: FiClipboard, label: "Review", route: "/review" },
  { icon: FiBookOpen, label: "Knowledge Base", route: "/knowledge-base" },
  { icon: FiLayers, label: "Templates", route: "/templates" },
  { icon: FiBarChart2, label: "Analytics", route: "/analytics" },
  { icon: FiSettings, label: "Settings", route: "/settings" },
];

export default function SidebarNav({
  items = defaultNavItems,
  selectedNav,
  onSelect,
  isMobile = false,
}) {
  const handleSelect = (item) => {
    if (onSelect) {
      onSelect(item);
    }
  };

  return (
    <>
      {!isMobile && (
        <div className="flex items-center gap-3 px-2 pb-7 pt-1">
          <Image
            src="/gitlab.jpg"
            alt="GitLab icon"
            width={48}
            height={48}
            className="h-10 w-10 rounded-sm object-cover sm:h-6 sm:w-6 lg:h-12 lg:w-12"
          />

          <div>
            <div className="text-[1.05rem] font-bold leading-none text-[#1f2328]">GitLab AI</div>
            <div className="mt-1 text-[0.72rem] font-medium text-[#6a707a]">
              Content &amp; Documentation Engine
            </div>
          </div>
        </div>
      )}

      <nav className="space-y-2">
        {items.map(({ icon: Icon, label, route }) => {
          const isActive = selectedNav === label;

          return (
            <button
              key={label}
              type="button"
              onClick={() => handleSelect({ label, route })}
              className={`hover:cursor-pointer group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-[1rem] font-medium transition-all duration-300 ease-out ${
                isActive
                  ? "translate-x-1 bg-[#fff0e8] text-[#d85c2a] shadow-[inset_0_0_0_1px_rgba(245,109,42,0.18)]"
                  : "text-[#3d434d] hover:-translate-x-1 hover:bg-[#fff4ee] hover:shadow-sm"
              }`}
            >
              <Icon
                className={`h-4 w-4 transition-transform duration-300 ${
                  isActive ? "translate-x-0.5" : "group-hover:translate-x-0.5"
                }`}
              />
              <span
                className={`transition-transform duration-300 ${
                  isActive ? "translate-x-0.5" : "group-hover:translate-x-0.5"
                }`}
              >
                {label}
              </span>
            </button>
          );
        })}
      </nav>

      {!isMobile && (
        <div className="mt-auto rounded-[18px] bg-[#fff0e8] p-4 text-[#693a1d] shadow-[inset_0_0_0_1px_rgba(245,109,42,0.14)]">
          <p className="text-[1.05rem] font-semibold leading-snug">“Better docs.</p>
          <p className="text-[1.05rem] font-semibold leading-snug">Faster releases.</p>
          <p className="mt-2 text-[1.05rem] font-semibold leading-snug">A stronger GitLab.”</p>
          <div className="mt-4 h-px w-full bg-[#d9e4f8]" />
          <p className="mt-3 text-[0.75rem] font-medium text-[#687387]">Build. Document. Together.</p>
        </div>
      )}
    </>
  );
}
