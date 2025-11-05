import React, { useState } from 'react';
import {
  Play, Package, X, Check, AlertCircle, Settings,
  Sparkles, Folder, Download, Trash2, Eye
} from 'lucide-react';
import {
  Button, Badge, IconButton, StatusBadge,
  EmptyState, Select, Modal, Tooltip
} from '../common';
import type { SelectOption } from '../common/Select';

/**
 * ComponentShowcase - Demo page for all reusable UI components
 *
 * This page demonstrates all the common components available in the kit_playground UI,
 * showing their various props, variants, and use cases.
 */
export const ComponentShowcase: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState('option1');

  const selectOptions: SelectOption[] = [
    { value: 'option1', label: 'Option 1', description: 'First option' },
    { value: 'option2', label: 'Option 2', badge: 'Recommended' },
    { value: 'option3', label: 'Option 3', description: 'Third option' },
    { value: 'option4', label: 'Disabled Option', disabled: true },
  ];

  return (
    <div className="flex flex-col h-full bg-bg-panel overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-border-subtle bg-bg-dark">
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          Component Showcase
        </h1>
        <p className="text-text-secondary">
          Reusable UI components for Kit Playground
        </p>
      </div>

      <div className="p-6 space-y-12">
        {/* Button Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">Button</h2>
          <p className="text-text-secondary mb-4">
            Primary action buttons with variants, sizes, and loading states
          </p>

          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Variants
              </h3>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="ghost">Ghost</Button>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Sizes
              </h3>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>

            {/* With Icons */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                With Icons
              </h3>
              <div className="flex flex-wrap gap-3">
                <Button icon={<Play />}>Launch</Button>
                <Button icon={<Package />} variant="secondary">Package</Button>
                <Button icon={<Download />} variant="primary">Download</Button>
              </div>
            </div>

            {/* Loading State */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Loading State
              </h3>
              <div className="flex flex-wrap gap-3">
                <Button loading>Loading...</Button>
                <Button loading variant="secondary">Processing...</Button>
              </div>
            </div>
          </div>
        </section>

        {/* IconButton Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">IconButton</h2>
          <p className="text-text-secondary mb-4">
            Icon-only buttons for compact actions
          </p>

          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Variants
              </h3>
              <div className="flex flex-wrap gap-3">
                <IconButton icon={<Settings />} variant="ghost" tooltip="Settings" />
                <IconButton icon={<Play />} variant="primary" tooltip="Play" />
                <IconButton icon={<Trash2 />} variant="danger" tooltip="Delete" />
                <IconButton icon={<Eye />} variant="secondary" tooltip="View" />
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Sizes
              </h3>
              <div className="flex flex-wrap items-center gap-3">
                <IconButton icon={<X />} size="sm" variant="ghost" />
                <IconButton icon={<X />} size="md" variant="ghost" />
                <IconButton icon={<X />} size="lg" variant="ghost" />
              </div>
            </div>
          </div>
        </section>

        {/* StatusBadge Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">StatusBadge</h2>
          <p className="text-text-secondary mb-4">
            Status indicators for jobs and projects
          </p>

          <div className="space-y-6">
            {/* Job Statuses */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Job Statuses
              </h3>
              <div className="flex flex-wrap gap-3">
                <StatusBadge status="pending" />
                <StatusBadge status="running" />
                <StatusBadge status="completed" />
                <StatusBadge status="failed" />
                <StatusBadge status="cancelled" />
              </div>
            </div>

            {/* Project Statuses */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Project Statuses
              </h3>
              <div className="flex flex-wrap gap-3">
                <StatusBadge status="created" />
                <StatusBadge status="built" />
                <StatusBadge status="running" />
                <StatusBadge status="failed" />
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Sizes
              </h3>
              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge status="running" size="sm" />
                <StatusBadge status="running" size="md" />
                <StatusBadge status="running" size="lg" />
              </div>
            </div>

            {/* Icon/Label Options */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Icon/Label Options
              </h3>
              <div className="flex flex-wrap gap-3">
                <StatusBadge status="completed" showIcon showLabel />
                <StatusBadge status="completed" showIcon={false} showLabel />
                <StatusBadge status="completed" showIcon showLabel={false} />
              </div>
            </div>
          </div>
        </section>

        {/* Badge Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">Badge</h2>
          <p className="text-text-secondary mb-4">
            Generic badges for tags, labels, and indicators
          </p>

          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Variants
              </h3>
              <div className="flex flex-wrap gap-3">
                <Badge variant="default">Default</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="error">Error</Badge>
                <Badge variant="info">Info</Badge>
                <Badge variant="nvidia">NVIDIA</Badge>
              </div>
            </div>

            {/* With Icons */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                With Icons
              </h3>
              <div className="flex flex-wrap gap-3">
                <Badge icon={<Sparkles className="w-3 h-3" />} variant="nvidia">Featured</Badge>
                <Badge icon={<Check className="w-3 h-3" />} variant="success">Verified</Badge>
                <Badge icon={<AlertCircle className="w-3 h-3" />} variant="warning">Beta</Badge>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
                Sizes
              </h3>
              <div className="flex flex-wrap items-center gap-3">
                <Badge size="sm">Small</Badge>
                <Badge size="md">Medium</Badge>
                <Badge size="lg">Large</Badge>
              </div>
            </div>
          </div>
        </section>

        {/* Select Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">Select</h2>
          <p className="text-text-secondary mb-4">
            Styled dropdown component with support for options, badges, and helper text
          </p>

          <div className="space-y-6 max-w-md">
            <Select
              label="Choose an option"
              options={selectOptions}
              value={selectedValue}
              onChange={setSelectedValue}
              helperText="This is a helper text"
            />

            <Select
              label="With error"
              options={selectOptions}
              value=""
              onChange={() => {}}
              error="This field is required"
            />

            <Select
              label="Disabled"
              options={selectOptions}
              value="option1"
              onChange={() => {}}
              disabled
            />
          </div>
        </section>

        {/* EmptyState Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">EmptyState</h2>
          <p className="text-text-secondary mb-4">
            Consistent empty state component with icon, title, description, and action button
          </p>

          <div className="space-y-8">
            <div className="p-6 border border-border-subtle rounded-lg bg-bg-card">
              <EmptyState
                icon={<Folder className="w-16 h-16" />}
                title="No projects yet"
                description="Create your first project to get started with Kit development"
                action={{
                  label: "Create Project",
                  onClick: () => alert('Create project clicked'),
                  icon: <Sparkles />,
                }}
              />
            </div>

            <div className="p-6 border border-border-subtle rounded-lg bg-bg-card">
              <EmptyState
                icon={<Package className="w-16 h-16" />}
                title="No packages found"
                description="You haven't created any packages yet"
              />
            </div>
          </div>
        </section>

        {/* Modal Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">Modal</h2>
          <p className="text-text-secondary mb-4">
            Full-featured modal dialog with escape key, overlay click, and body scroll lock
          </p>

          <div className="space-y-6">
            <Button onClick={() => setIsModalOpen(true)}>Open Modal</Button>

            <Modal
              isOpen={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              title="Example Modal"
              actions={
                <>
                  <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                    Confirm
                  </Button>
                </>
              }
            >
              <div className="space-y-4">
                <p className="text-text-primary">
                  This is an example modal dialog. It supports:
                </p>
                <ul className="list-disc list-inside text-text-secondary space-y-2">
                  <li>Escape key to close</li>
                  <li>Overlay click to close (configurable)</li>
                  <li>Body scroll lock when open</li>
                  <li>Custom actions footer</li>
                  <li>Multiple sizes (sm, md, lg, xl)</li>
                </ul>
              </div>
            </Modal>
          </div>
        </section>

        {/* Tooltip Component */}
        <section>
          <h2 className="text-xl font-bold text-text-primary mb-4">Tooltip</h2>
          <p className="text-text-secondary mb-4">
            Hover tooltip component with 4 position options and configurable delay
          </p>

          <div className="space-y-6">
            <div className="flex flex-wrap gap-8">
              <Tooltip content="Top tooltip" position="top">
                <Button variant="secondary">Hover (Top)</Button>
              </Tooltip>

              <Tooltip content="Bottom tooltip" position="bottom">
                <Button variant="secondary">Hover (Bottom)</Button>
              </Tooltip>

              <Tooltip content="Left tooltip" position="left">
                <Button variant="secondary">Hover (Left)</Button>
              </Tooltip>

              <Tooltip content="Right tooltip" position="right">
                <Button variant="secondary">Hover (Right)</Button>
              </Tooltip>
            </div>

            <div>
              <Tooltip content="This tooltip has a custom delay" delay={500}>
                <Button variant="secondary">Hover (Custom Delay: 500ms)</Button>
              </Tooltip>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ComponentShowcase;
