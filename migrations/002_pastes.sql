-- Add parent_revision column to paste revision table.
-- This allows us to fork or edit a specific revision of a paste, rather than just the base

ALTER TABLE `revisions`
    ADD `parent_revision` INT NULL;

-- Allow message to be longer than 255 characters.
-- Enforced to be < 1024 on the server

ALTER TABLE `revisions`
    MODIFY `message` TEXT NULL;
