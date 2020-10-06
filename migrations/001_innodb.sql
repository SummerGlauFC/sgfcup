-- Switch to InnoDB so we can use foreign keys

ALTER TABLE `accounts`
    ENGINE = InnoDB;
ALTER TABLE `files`
    ENGINE = InnoDB;
ALTER TABLE `pastes`
    ENGINE = InnoDB;
ALTER TABLE `revisions`
    ENGINE = InnoDB;
ALTER TABLE `settings`
    ENGINE = InnoDB;