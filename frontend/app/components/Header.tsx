interface HeaderProps {
  title: string;
  description: string;
}

export function Header({ title, description }: HeaderProps) {
  return (
    <header className="space-y-1">
      <h1 className="text-3xl font-semibold">{title}</h1>
      <p className="text-gray-600">{description}</p>
    </header>
  );
}
