-- Create users table
create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  jellyfish_id text references jellyfish(id),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Create jellyfish table
create table jellyfish (
  id text primary key,
  name text not null,
  email text references users(email),
  birth_date timestamp with time zone not null,
  color text not null,
  personality_traits text[],
  look_dna jsonb,
  founder_glow boolean default false,
  last_tap timestamp with time zone,
  traits text[],
  secret_key text unique,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Create index on jellyfish email for lookups
create index idx_jellyfish_email on jellyfish(email);

-- Create registry view for public display
create view jellyfish_registry as
select 
  id,
  name,
  birth_date,
  color,
  personality_traits,
  traits,
  founder_glow,
  row_number() over (order by birth_date) as registry_number
from jellyfish;

-- Enable Row Level Security
alter table users enable row level security;
alter table jellyfish enable row level security;

-- Create policies for public registry
create policy "Public jellyfish registry"
  on jellyfish for select
  using (true);

create policy "Allow signups"
  on users for insert
  with check (email is not null);

create policy "Allow profile updates"
  on users for update
  using (auth.uid() = id);